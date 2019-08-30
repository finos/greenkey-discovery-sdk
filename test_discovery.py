#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
"""
from fire import Fire
import fnmatch
import json
import logging
import os
import requests
import subprocess
import sys
import time
import yaml
import operator
from functools import reduce
from collections import defaultdict
from os.path import abspath, exists, join as join_path

import editdistance
from metrics import compute_all
from parse_tests import load_tests, load_test_file, find_whitelists

from discovery_config import (
    CONTAINER_NAME,
    DISCOVERY_CONFIG,
    DISCOVERY_HOST,
    DISCOVERY_PORT,
    DISCOVERY_SHUTDOWN_SECRET,
    RETRIES,
    TIMEOUT,
)
from launch_discovery import launch_discovery

DISCOVERY_URL = "http://{}:{}/process".format(DISCOVERY_HOST, DISCOVERY_PORT)

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(lineno)d %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

file_handler = logging.FileHandler("test_discovery.log")
file_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


"""
Functions for handling the Discovery Docker container
"""


def docker_log_and_stop(volume=None):
    """
    name assigned to Docker container; modify CONTAINER_NAME in
    discovery_config.py
        default='discovery-dev'
    """
    subprocess.call("docker logs {}".format(CONTAINER_NAME), shell=True)
    subprocess.call("docker stop {}".format(CONTAINER_NAME), shell=True)
    if volume is not None:
        subprocess.call("docker volume rm {}".format(volume), shell=True)


def check_discovery_status():
    """
    Checks whether Discovery is ready to receive new jobs
    """
    r = requests.get("http://{}:{}/status".format(DISCOVERY_HOST, DISCOVERY_PORT))
    return True if "listening" in r.json()["message"] else False


def wait_for_discovery_status():
    """
    Wait for Discovery to be ready
    """
    for i in range(RETRIES):
        try:
            check_discovery_status()
            return True
        except Exception:
            if i >= 3:
                logger.error("Could not reach discovery, attempt {0} of {1}".format(
                    i + 1, RETRIES))
            time.sleep(TIMEOUT)
    return False


def wait_for_discovery_launch():
    """
    Wait for launch to complete
    """
    # Timeout of 25 seconds for launch
    if not wait_for_discovery_status():
        print("Couldn't launch Discovery, printing Docker logs:\n---\n")
        docker_log_and_stop()
        sys.exit(1)
    else:
        print("Discovery Launched!")


def shutdown_discovery(shutdown=True):
    """
    Shuts down the Discovery engine Docker container
    """
    if not shutdown:
        return

    print("\nShutting down Discovery\n")
    try:
        requests.get("http://{}:{}/shutdown?secret_key={}".format(
            DISCOVERY_HOST, DISCOVERY_PORT, DISCOVERY_SHUTDOWN_SECRET))
    # Windows throws a ConnectionError for a request to shutdown a server which makes it looks like the test fail
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(3)


"""
Testing functions
"""


def json_dump(data, outfile, directory=None):
    """
    :param data: json serializable object
    :param outfile: str; name of output file
    :param directory: str (optional);
    :return: saves data to file named outfile in directory (or current dir if unspecified)
    """
    if not directory:
        directory = os.getcwd()
    outfile = join_path(directory, outfile)
    json.dump(data, open(outfile, "w+"), indent=2)


def submit_transcript(transcript, intent_whitelist="any", domain_whitelist="any"):
    """
    Submits a transcript to Discovery
    :param transcript: str,
    :param intent_whitelist: str; 'any' (default) or list of intent labels (if intent_whitelist in test_file)
    :param domain_whitelist: str: 'any' (default) or list of domain labels (if domain_whitelist in test_file)
    """
    payload = {
        "transcript": transcript,
        "intents": intent_whitelist,
        "domains": domain_whitelist,
    }
    response = requests.post(DISCOVERY_URL, json=payload)
    if not response.status_code == 200:
        logger.error("Request was not successful. Response Status Code: {}".format(
            response.status_code))
        return {}
    return response.json()


def is_valid_response(resp):
    """
    Validates a Discovery response
    Fail if a failure response was received
    """
    request_failed = "result" in resp and resp["result"] == "failure"
    missing_intent_or_entity = not ("intents" in resp and resp["intents"]
                                    and resp["intents"][0])
    if request_failed or missing_intent_or_entity:
        return False
    return True


def test_single_entity(entities, test_name, test_value):
    """
    Tests a single entity within a test case
    :param entities:
    :param test_name:
    :param test_value: str, expected substrings for
    """
    if test_name not in entities.keys():
        msg = "Entity not found: {}".format(test_name)
        fail_test({}, msg, continued=True)
        logger.info(msg)
        return 1, len(test_value)

    if entities[test_name] != test_value:
        msg = "\nObserved Entity Value Incorrect: ({}) Expected {} != {}".format(
            test_name, test_value, entities[test_name])
        fail_test({}, msg, continued=True)
        logger.info(msg)
        return 1, editdistance.eval(test_value, entities[test_name])
    return 0, 0


def test_schema(full_response, test_value):
    """
    For each key-value pair given in the schema test,
    recursively search the JSON response for the key,
    then make sure the value is correct
    """

    def _find(obj, key):
        if isinstance(obj, list):
            for list_item in obj:
                item = _find(list_item, key)
                if item is not None:
                    return item
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            for k, v in obj.items():
                item = _find(v, key)
                if item is not None:
                    return item

    # Returning number of errors, so check for values that do not equal test case
    errs = {}
    for res in map(
            lambda k: {k: _find(full_response, k)} if _find(full_response, k) !=
            test_value[k] else {}, list(test_value.keys())):
        errs.update(res)
    return errs


def strip_extra_whitespace(payload):
    """
    Cut leading and trailing whitespace as well as double spaces everywhere
    Accepts lists, strings, and dictionaries
    >>> strip_extra_whitespace("this is  a cat")
    'this is a cat'
    >>> strip_extra_whitespace(" this is a cat")
    'this is a cat'
    >>> strip_extra_whitespace({"transcript": "euro five week         "})
    {'transcript': 'euro five week'}
    """

    if isinstance(payload, str):
        while "  " in payload:
            payload = payload.replace("  ", " ")
        payload = payload.strip()
    elif isinstance(payload, list):
        payload = [strip_extra_whitespace(v) for v in payload]
    elif isinstance(payload, dict):
        for k, v in payload.items():
            payload.pop(k)
            payload[strip_extra_whitespace(k)] = strip_extra_whitespace(v)
    return payload


def test_single_case(test_dict, observed_entity_dict, full_response, verbose=False):
    """
    Run a single test case and return the number of errors

    :param test_dict: dict;
    key: str; name of entity
    value: str; first occurrence of entity in transcript

    :param observed_entity_dict: dict, single intent from Discovery response
    :return: Tuple(bool, int, int, int)
        first element: bool; 0 if tests pass, 1 if tests fails
        total_errors: int; number of entities in test whose observed value (str) differs from expected
        total_char_errors: int; sum of number of characters that differ between observed and expected values for each entity
        characters: int; length of expected entity label (test_value)
    """
    total_errors = 0
    total_char_errors = 0
    characters = 0

    # Loop through all entity tests
    for label, value in test_dict.items():
        if label in ["test", "transcript", "intent"]:
            continue
        entity_label, expected_entity_value = map(strip_extra_whitespace, [label, value])
        full_response = strip_extra_whitespace(full_response)

        if entity_label == "schema":
            errors = test_schema(
                full_response=full_response,
                test_value=json.loads(expected_entity_value),
            )
            if errors:
                print("\nSchema test failed for {} with response {}\n".format(
                    expected_entity_value, errors))
                if verbose:
                    print("Full response is {}".format(full_response))
            errors = len(errors)
        else:
            (errors, char_errors) = test_single_entity(
                entities=observed_entity_dict,
                test_name=entity_label,
                test_value=expected_entity_value,
            )
            total_char_errors += char_errors
            characters += len(expected_entity_value)
        total_errors += errors

    # entities found by discovery but not specified in test file
    extra_entities = {
        x: observed_entity_dict[x]
        for x in observed_entity_dict if x not in test_dict
    }

    if extra_entities and verbose:
        extra_entities_msg = "Extra entities: {}\n".format(extra_entities)
        logger.info(extra_entities_msg)
        print(extra_entities_msg)

    if total_errors:
        return 1, total_errors, total_char_errors, characters
    else:
        print("Entity Tests passed\n---\n")
        return 0, 0, 0, characters


def test_all(test_file, verbose=False):
    """
    Runs all defined tests
    Compares expected intent and entities (from test) with discovery returned intents and entities

    :param test_file: str, test file

    Optional: Prior to tests, can list permitted intents and/or domains as comma separated strings.
    - If included, value(s) will be passed with each request; else default 'any'
        intent_whitelist: intent1, intent2
        domain_whitelist: domain1,

    Each test:
        test: name of test
        transcript: text to send to discovery
    valid tests must include at least one of the following:
        intent: name of intent (only one label for each intent tested)
        entity_name: text that Discovery identified as an instance of the entity
        - can include as many entities as defined for a given intent

    :return
        prints to stdout
        (1) the number of tests that pass
        (2) the time it took to run the tests
        (3) total number of character errors in entities tested
        (4) the entity character error rate

    saves 2 json files:
        (1) test_results.json: contains expected intent labels and corresponding model predicted labels
        (2) test_metrics.json: computes precision, recall, f1_score and accuracy is possible; else returns accuracy and count confusion matrix
    """
    tests, intent_whitelist, domain_whitelist = load_tests(test_file)

    t1 = int(time.time())

    total_tests = len(tests)

    failed_tests = total_errors = total_char_errors = total_characters = 0
    y_true = []
    y_pred = []
    output_dict = defaultdict(dict)

    # for test_no, test in enumerate(tests):
    for test_no, test_dict in enumerate(tests):
        test_name, transcript = test_dict["test"], test_dict["transcript"]

        test_start_msg = "======\nTest: {}".format(test_name)
        logger.info(test_start_msg)

        resp = submit_transcript(transcript, intent_whitelist, domain_whitelist)

        # Check if a valid response was received
        if not is_valid_response(resp):
            fail_test(resp)

        # keep only the most likely hypothesis from Discovery    -> first dict in list of dicts returned by Discovery
        most_likely_intent = resp["intents"][0]

        if "intent" in test_dict:
            expected_intent = test_dict["intent"]
            observed_intent = most_likely_intent["label"]

            y_true.append(expected_intent)
            y_pred.append(observed_intent)
            correct = 1 if expected_intent == observed_intent else 0

            output_dict[test_no] = dict(
                test_name=test_name,
                transcript=transcript,
                expected_intent=expected_intent,
                observed_intent=observed_intent,
                correct=(1 if expected_intent == observed_intent else 0),
            )

            logger.info("\nExpected Intent: {} \nObserved Intent{}".format(
                expected_intent, observed_intent))

            if expected_intent != observed_intent:
                observed_not_expected_msg = "Observed intent does not match expected intent!"
                failed_tests += 1
                fail_test(resp,
                          message="Observed intent does not match expected intent!",
                          continued=True)

        ################################################################################################################
        # Get all values of all entities returned by discovery for a test transcript
        entities_found = most_likely_intent["entities"]
        observed_entity_dict = {
            ent["label"]: ent["matches"][0][0]["value"]
            for ent in entities_found
        }
        # Remove non-entity keys from test_dict, then pass to `test_single_case`
        for label in ["test", "transcript", "intent"]:
            try:
                del observed_entity_dict[label]
                del test_dict[label]
            except KeyError:
                continue
        output_dict[test_no]["expected_entities"] = test_dict
        output_dict[test_no]["observed_entities"] = observed_entity_dict

        ################################################################################################################
        # Start Testing Entities for Test case : test_no
        (failure, errors, char_errors,
         characters) = test_single_case(test_dict, observed_entity_dict, resp, verbose)
        failed_tests += failure
        total_errors += errors
        total_char_errors += char_errors
        total_characters += characters

    ####################################################################################################################
    # All tests complete
    ####################################################################################################################
    time_lapsed = int(time.time()) - t1
    total_entity_character_errors = total_errors
    correct_tests = total_tests - failed_tests
    accuracy = (correct_tests / total_tests) * 100

    output_dir = os.path.dirname(test_file)

    # save output variables computed across tests
    summary_dict = dict(total_tests=total_tests,
                        test_time_sec=time_lapsed,
                        expected_intents=y_true,
                        observed_intents=y_pred,
                        total_entity_character_errors=total_errors,
                        total_character_errors=total_char_errors,
                        total_characters=total_characters,
                        accuracy=accuracy)
    output_dict.update(summary_dict)
    json_dump(data=output_dict, outfile='test_results.json', directory=output_dir)

    # record message regardless of number of entity errors
    message = "\n---\n({} / {}) tests passed in {} seconds from {}".format(
        correct_tests, total_tests, time_lapsed, test_file)
    logger.info(message)
    print(message)

    if total_characters:
        entity_character_error_rate = 100 * (total_char_errors / total_characters)
        msg = "\nTotal number of entity character errors: {} \nEntity Character Error Rate: {}".format(
            total_entity_character_errors, "{:.2f}".format(entity_character_error_rate))
        logger.info(msg)
        print(msg)

    # evaluate metrics; treat each possible intent as reference
    metrics_dict = compute_all(y_true, y_pred)
    json_dump(metrics_dict, outfile="test_metrics.json")

    # # total_errors
    if total_entity_character_errors > 0:
        logger.error("\nTotal entity characters found: {}".format(total_entity_character_errors))
        
    if total_tests > correct_tests:
        return False
      
    return True


def fail_test(resp, message="", continued=False):
    print("Test failed: " + message)
    print("{}\n---\n".format(resp))
    if not continued:
        docker_log_and_stop()
        sys.exit(1)


"""
Interpreter validation
"""


def validate_yaml(intents_config_file):
    """
    Validate definitions.yaml
    """
    try:
        with open(intents_config_file) as f:
            yaml_file_contents = f.read()
            yaml.load(yaml_file_contents, Loader=yaml.FullLoader)
    except Exception as e:
        print("Invalid definitions.yaml file")
        print("Error: {}".format(e))
        sys.exit(1)
    return True


def make_sure_directories_exist(directories):
    for d in directories:
        try:
            assert exists(d)
        except AssertionError:
            logger.exception("Error: Check path to directory: {}".format(d),
                             exc_info=True)
            print("Terminating program")
            sys.exit(1)


def add_extension_if_missing(test_file):
    """
    Add .txt extension if not present
    >>> add_extension_if_missing('this')
    "this.txt"
    >>> add_extension_if_missing('that.txt')
    "that.txt"
    """
    if not test_file.endswith(".txt"):
        test_file += ".txt"
    return test_file


def limit_discovery_domains(directory, tests):
    domains = (find_whitelists(
        load_test_file(join_path(directory, add_extension_if_missing(f))))[2]
               for f in (tests.split(",") if isinstance(tests, str) else tests))
    flattened_domains = ','.join(
        list(filter(lambda x: x is not "any", set((i for s in domains for i in s)))))
    if flattened_domains:
        DISCOVERY_CONFIG['DISCOVERY_DOMAINS'] = flattened_domains
        print("Limiting domains to {}".format(flattened_domains))


def main(directory=os.getcwd(), tests="tests.txt", shutdown=True, help=False, verbose=False):
    """
    :param directory: Path to directory containing custom/ directory
    :param tests: Comma separated list of file(s) containing tests
    :param shutdown: Whether to stop Discovery container after testing
    :param help: prints this help message
    :param verbose: print extra entities found
    :return: loads yaml definitions files, launches discovery, trains custom interpreters, posts each test in tests
        and saves results + computed metrics
    """
    if help:
        print("Test discovery usage: ")
        print(main.__doc__)
        sys.exit(0)

    custom_directory = join_path(abspath(directory), "custom")
    make_sure_directories_exist([directory, custom_directory])

    try:
        assert exists(directory) and exists(custom_directory)
    except AssertionError:
        logger.exception(
            "Error: Check path to custom directory: {}".format(custom_directory),
            exc_info=True,
        )
        print("Terminating program")
        sys.exit(1)

    # get all definition yaml files
    for yml_file in fnmatch.filter(custom_directory, ".yaml"):
        validate_yaml(join_path(custom_directory, yml_file))

    success = False
    volume = None
    try:
        limit_discovery_domains(directory, tests)
        volume = launch_discovery(custom_directory=custom_directory)
        wait_for_discovery_launch()

        success = all(
            test_all(join_path(directory, add_extension_if_missing(test_file)), verbose)
            for test_file in (tests.split(",") if isinstance(tests, str) else tests))
    except Exception:
        logger.exception("Error: Check test files for formatting errors", exc_info=True)

    docker_log_and_stop(volume) if (not success and os.environ.get(
        'OUTPUT_FAILED_LOGS', False)) else shutdown_discovery(shutdown)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    Fire(main)
