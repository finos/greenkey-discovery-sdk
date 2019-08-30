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


def request_failed(resp):
    return "result" in resp and resp["result"] == "failure"


def missing_intent_or_entity(resp):
    return not ("intents" in resp and resp["intents"] and resp["intents"][0])


def is_valid_response(resp):
    """
    Validates a Discovery response
    Fail if a failure response was received
    """
    return False if request_failed(resp) or missing_intent_or_entity(resp) else True


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


def print_schema_errors(expected_entity_value, errors, full_response, verbose=False):
    print("\nSchema test failed for {} with response {}\n".format(
        expected_entity_value, errors))
    if verbose:
        print("Full response is {}".format(full_response))
    errors = len(errors)


def _find_in_list(obj, key):
    for list_item in obj:
        item = _find(list_item, key)
        if item is not None:
            return item


def _find_in_dict(obj, key):
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        item = _find(v, key)
        if item is not None:
            return item


def _find(obj, key):
    if isinstance(obj, list):
        return _find_in_list(obj, key)
    if isinstance(obj, dict):
        return _find_in_dict(obj, key)


def test_schema(full_response, test_value, verbose=False):
    """
    For each key-value pair given in the schema test,
    recursively search the JSON response for the key,
    then make sure the value is correct
    """

    # Returning number of errors, so check for values that do not equal test case
    errs = {}
    for res in map(
            lambda k: {k: _find(full_response, k)}
            if _find(full_response, k) != test_value[k] else {},
            list(test_value.keys()),
    ):
        errs.update(res)

    if errs:
        print_schema_errors(test_value, errs, full_response, verbose)

    return len(errs)


def remove_all_whitespace_from_string(input_string):
    while "  " in input_string:
        input_string = input_string.replace("  ", " ")
    return input_string.strip()


def clean_list(input_list):
    return [strip_extra_whitespace(v) for v in input_list]


def clean_dict(input_dict):
    output_dict = {}
    for k, v in input_dict.items():
        output_dict[strip_extra_whitespace(k)] = strip_extra_whitespace(v)
    return output_dict


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
        payload = remove_all_whitespace_from_string(payload)
    elif isinstance(payload, list):
        payload = clean_list(payload)
    elif isinstance(payload, dict):
        payload = clean_dict(payload)
    return payload


def print_extra_entities(observed_entity_dict, test_dict):
    """ prints entities found by discovery but not specified in test file """
    extra_entities = {
        x: observed_entity_dict[x]
        for x in observed_entity_dict if x not in test_dict
    }

    if extra_entities:
        extra_entities_msg = "Extra entities: {}\n".format(extra_entities)
        logger.info(extra_entities_msg)
        print(extra_entities_msg)


def run_test_dict(
        full_response,
        observed_entity_dict,
        entity_label,
        expected_entity_value,
        verbose=False,
):
    char_errors = 0
    if entity_label == "schema":
        errors = test_schema(full_response, json.loads(expected_entity_value), verbose)
    else:
        (errors, char_errors) = test_single_entity(observed_entity_dict, entity_label,
                                                   expected_entity_value)
    return errors, char_errors, len(expected_entity_value)


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
    total_characters = 0

    # Loop through all entity tests
    for label, value in test_dict.items():
        if label in ["test", "transcript", "intent"]:
            continue
        entity_label, expected_entity_value = map(strip_extra_whitespace, [label, value])
        full_response = strip_extra_whitespace(full_response)
        errors, char_errors, characters = run_test_dict(
            full_response,
            observed_entity_dict,
            entity_label,
            expected_entity_value,
            verbose,
        )

        total_errors += errors
        total_char_errors += char_errors
        total_characters += characters

    if verbose:
        print_extra_entities(observed_entity_dict, test_dict)

    return (
        (1 if total_errors else 0),
        total_errors,
        total_char_errors,
        total_characters,
        observed_entity_dict,
    )


def format_intent_test_result(test_name, transcript, expected_intent, observed_intent):
    return dict(
        test_name=test_name,
        transcript=transcript,
        expected_intent=expected_intent,
        observed_intent=observed_intent,
        correct=(1 if expected_intent == observed_intent else 0),
    )


def evaluate_intent(test_dict, resp, test_name, test_no):

    failed_test = 0

    expected_intent = test_dict["intent"]
    # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
    observed_intent = resp["intents"][0]["label"]

    logger.info("\nExpected Intent: {} \nObserved Intent{}".format(
        expected_intent, observed_intent))

    if expected_intent != observed_intent:
        failed_test = 1
        fail_test(
            resp,
            message="Observed intent does not match expected intent!",
            continued=True,
        )
    return failed_test, expected_intent, observed_intent


def evaluate_entities(test_dict, resp, verbose):
    most_likely_entities = resp["intents"][0]["entities"]
    observed_entity_dict = {
        # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
        ent["label"]: ent["matches"][0][0]["value"]
        for ent in most_likely_entities
    }
    # Remove non-entity keys from test_dict, then pass to `test_single_case`
    for label in ["test", "transcript", "intent"]:
        try:
            del observed_entity_dict[label]
            del test_dict[label]
        except KeyError:
            continue

    ################################################################################################################
    # Start Testing Entities for Test case : test_no
    return test_single_case(test_dict, observed_entity_dict, resp, verbose)


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

    for test_no, test_dict in enumerate(tests):
        test_name, transcript = test_dict["test"], test_dict["transcript"]

        test_start_msg = "======\nTest: {}".format(test_name)
        logger.info(test_start_msg)

        resp = submit_transcript(transcript, intent_whitelist, domain_whitelist)

        # Check if a valid response was received
        if not is_valid_response(resp):
            fail_test(resp)

        if "intent" in test_dict:
            failed_test, expected_intent, observed_intent = evaluate_intent(
                test_dict, resp, test_name, test_no)
            failed_tests += failed_test
            output_dict[test_no] = format_intent_test_result(test_name, transcript,
                                                             expected_intent,
                                                             observed_intent)
            y_true.append(expected_intent)
            y_pred.append(observed_intent)

        ################################################################################################################
        # Get all values of all entities returned by discovery for a test transcript
        (
            failure,
            errors,
            char_errors,
            characters,
            observed_entity_dict,
        ) = evaluate_entities(test_dict, resp, verbose)
        output_dict[test_no]["expected_entities"] = test_dict
        output_dict[test_no]["observed_entities"] = observed_entity_dict

        failed_tests += failure
        total_errors += errors
        total_char_errors += char_errors
        total_characters += characters

    ####################################################################################################################
    # All tests complete
    ####################################################################################################################
    time_lapsed = int(time.time()) - t1
    correct_tests = total_tests - failed_tests
    accuracy = (correct_tests / total_tests) * 100

    # save output variables computed across tests
    summary_dict = dict(
        total_tests=total_tests,
        test_time_sec=time_lapsed,
        expected_intents=y_true,
        observed_intents=y_pred,
        total_entity_character_errors=total_errors,
        total_character_errors=total_char_errors,
        total_characters=total_characters,
        correct_tests=correct_tests,
        test_file=test_file,
        accuracy=accuracy,
    )
    output_dict.update(summary_dict)

    return record_results(output_dict)


def record_results(output_dict):
    output_dir = os.path.dirname(output_dict["test_file"])
    json_dump(data=output_dict, outfile="test_results.json", directory=output_dir)

    # record message regardless of number of entity errors
    message = "\n---\n({} / {}) tests passed in {} seconds from {}".format(
        output_dict["correct_tests"],
        output_dict["total_tests"],
        output_dict["test_time_sec"],
        output_dict["test_file"],
    )
    logger.info(message)
    print(message)

    if "total_characters" in output_dict and output_dict["total_characters"]:
        entity_character_error_rate = 100 * (output_dict["total_character_errors"] /
                                             output_dict["total_characters"])
        msg = "\nTotal number of entity character errors: {} \nEntity Character Error Rate: {}".format(
            output_dict["total_entity_character_errors"],
            "{:.2f}".format(entity_character_error_rate),
        )
        logger.info(msg)
        print(msg)

    # evaluate metrics; treat each possible intent as reference
    metrics_dict = compute_all(output_dict["expected_intents"],
                               output_dict["observed_intents"])
    json_dump(metrics_dict, outfile="test_metrics.json")

    # # total_errors
    if output_dict["total_entity_character_errors"] > 0:
        logger.error("\nTotal entity characters found: {}".format(
            output_dict["total_entity_character_errors"]))

    if output_dict["total_tests"] > output_dict["correct_tests"]:
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


def report_domain_whitelists(directory, tests):
    return (find_whitelists(
        load_test_file(join_path(directory, add_extension_if_missing(f))))[2]
            for f in (tests.split(",") if isinstance(tests, str) else tests))


def limit_discovery_domains(directory, tests):
    domains = report_domain_whitelists(directory, tests)

    flattened_domains = ",".join(
        list(filter(lambda x: x is not "any", set((i for s in domains for i in s)))))

    if flattened_domains:
        DISCOVERY_CONFIG["DISCOVERY_DOMAINS"] = flattened_domains
        print("Limiting domains to {}".format(flattened_domains))


def print_help():
    print("Test discovery usage: ")
    print(main.__doc__)
    sys.exit(0)


def validate_directory_exists(directory):
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
    return custom_directory


def setup_discovery(directory, custom_directory, tests):
    limit_discovery_domains(directory, tests)
    volume = launch_discovery(custom_directory=custom_directory)
    wait_for_discovery_launch()
    return volume


def evaluate_all_tests(directory, tests, verbose=False):
    return all(
        test_all(join_path(directory, add_extension_if_missing(test_file)), verbose)
        for test_file in (tests.split(",") if isinstance(tests, str) else tests))


def run_all_tests_in_directory(directory, custom_directory, tests, shutdown, verbose):
    success = False
    volume = None
    try:
        volume = setup_discovery(directory, custom_directory, tests)
        success = evaluate_all_tests(directory, tests, verbose)
    except Exception:
        logger.exception("Error: Check test files for formatting errors", exc_info=True)

    docker_log_and_stop(volume) if (not success and os.environ.get(
        "OUTPUT_FAILED_LOGS", False)) else shutdown_discovery(shutdown)
    return success


def test_discovery(directory=os.getcwd(),
                   tests="tests.txt",
                   shutdown=True,
                   help=False,
                   verbose=False):
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
        print_help()

    custom_directory = validate_directory_exists(directory)

    # get all definition yaml files
    for yml_file in fnmatch.filter(custom_directory, ".yaml"):
        validate_yaml(join_path(custom_directory, yml_file))

    success = run_all_tests_in_directory(directory, custom_directory, tests, shutdown,
                                         verbose)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    Fire(test_discovery)
