#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
"""
import fnmatch
import json
import logging
import os
import requests
import subprocess
import sys
import time
import yaml
from collections import defaultdict, namedtuple
from os.path import abspath, exists, join as join_path

import editdistance
from fire import Fire
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
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
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


def try_discovery(attempt_number):
    try:
        check_discovery_status()
        return True
    except Exception:
        if attempt_number >= 3:
            logger.error("Could not reach discovery, attempt {0} of {1}".format(
                attempt_number + 1, RETRIES))
        time.sleep(TIMEOUT)


def wait_for_discovery_status():
    """
    Wait for Discovery to be ready
    """
    for attempt_number in range(RETRIES):
        if try_discovery(attempt_number):
            return True
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


def fail_test(resp, message="", continued=False):
    print("Test failed: " + message)
    print("{}\n---\n".format(resp))
    if not continued:
        docker_log_and_stop()
        sys.exit(1)


def print_extra_entities(observed_entity_dict, test_dict):
    """ prints entities found by discovery but not specified in test file
    :param observed_entity_dict: Dict, contains key 'label' and 'matches'
        the latter containing all token(s) Discovery identified as value of label
    :param test_dict: Dict, consists of user-specified entity labels & expected values
    :return: prints entity(ies) discovered by Discovery (in observed_entity_dict)
        that were not in the test_dict, if any
    """
    extra_entities = {
        x: observed_entity_dict[x]
        for x in observed_entity_dict if x not in test_dict
    }

    if extra_entities:
        extra_entities_msg = "Extra entities: {}\n".format(extra_entities)
        print(extra_entities_msg)


def print_schema_errors(expected_entity_value, errors, full_response, verbose=False):
    print("\nSchema test failed for {} with response {}\n".format(
        expected_entity_value, errors))
    if verbose:
        print("Full response is {}".format(full_response))


def _find_in_list(obj, key):
    for list_item in obj:
        item = _find(list_item, key)
        if item is not None:
            return item


def _find_in_dict(obj, key):
    if key in obj:
        return obj[key]
    for v in obj.values():
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
    :param full_response: Dict, jsonified value of request.Response object returned by
        Discovery (for posted transcript_
    :param test_value: str, value of key in JSON schema
    :param verbose: bool; default (False); prints whether the schema test for a given test
        passed; if True, also prints entire Dict (response from Discovery for posted transcript)
    :return: int, number of errors
        sum of expected values for JSON Schema test that were not found
            or the entity was found but contained the wrong value
    """
    # Returning number of errors, so check for values that do not equal test case
    errors = dict()
    for test_key, test_val in test_value.items():
        match = _find(obj=full_response, key=test_key)
        if match != test_val:
            errors[test_key] = match  # no need to call .update() or input empty dicts
    if errors:
        print_schema_errors(
            expected_entity_value=test_value,
            errors=errors,
            full_response=full_response,
            verbose=verbose)
    return len(errors)


def test_single_entity(entities, test_name, test_value):
    """
    Tests a single entity within a test case
    :param entities: Dict; containing all entities Discovery extracted
    keys: str, entity-label
    values: str, token(s) in string identified as instance of entity
    :param test_name: str, label of entity testing
    :param test_value: str, true token that is an instance of entity in transcript

    possible outcomes:
    1) failure: Discovery did not find the entity  -> test entity label (test_name) NOT in entities
    2) partial-failure: test entity label found in entities but corresponding value is incorrect
        measure of wrongness: edit distance between the test_value and value of test_name in entities
    3) success: Discovery found correct entity -> test_name in entities and value for key is test_value

    :return Tuple(int, int)
        first element indicates outcome: 1 for failure (outcome 1 & 2 above); 0 for success (outcome 3)
        second element - character error count:
            case 1: length of test_value since no overlap is possible as Discovery did not find entity
            case 3: 0 as the correct token(s) was identified
            case 2: measure given by edit distance between true and observed values
    """
    if test_name not in entities:  #.keys():
        msg = "Entity not found: {}".format(test_name)
        fail_test({}, msg, continued=True)
        # logger.info(msg)       # print & docker log ^ fail_test
        return 1, len(test_value)

    if entities[test_name] != test_value:
        msg = "\nObserved Entity Value Incorrect: ({}) Expected {} != {}".format(
            test_name, test_value, entities[test_name])
        fail_test({}, msg, continued=True)
        # logger.info(msg)
        return 1, editdistance.eval(test_value, entities[test_name])
    return 0, 0


def test_single_case(test_dict, observed_entity_dict, full_response, verbose=False):
    """
    Run a single test case and return the number of errors

    :param test_dict: dict;
        keys: str; name of entity
        values: str; first occurrence of entity in transcript

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
    for entity_label, expected_entity_value in test_dict.items():
        char_errors = 0

        if entity_label == "schema":
            errors = test_schema(full_response, json.loads(expected_entity_value),
                                 verbose)
        else:
            (errors, char_errors) = test_single_entity(
                observed_entity_dict, entity_label, expected_entity_value)

        total_errors += errors
        total_char_errors += char_errors
        total_characters += len(expected_entity_value)

    if verbose:
        print_extra_entities(observed_entity_dict, test_dict)

    return dict(
        failure=(1 if total_errors else 0),
        total_errors=total_errors,
        total_char_errors=total_char_errors,
        total_characters=total_characters,
        observed_entity_dict=observed_entity_dict,
    )


def evaluate_entities(test_dict, resp, verbose, num_intents=0):
    """
    :param test_dict: Dict, single test case (line in test file)
    :param resp: Dict, jsonified requests.Response object returned from Discovery
    :param verbose: bool, if True, prints not only whether entity test failed
        but entire response for all entities for top (first) intent
    :return: 4-Tuple, see test_single_test_case
        for a given test, tests whether each entity in test is present in
            response entities dict and, if so, whether observed value matches expected value
    """
    entities = most_likely_entities = resp["intents"][num_intents]["entities"]
    observed_entity_dict = {
        # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
        ent["label"]: ent["matches"][0][0]["value"]
        for ent in entities  #most_likely_entities
    }
    # Remove non-entity keys from test_dict, then pass to `test_single_case`
    test_dict = {
        k: v
        for k, v in test_dict.items() if not k in ['test', 'transcript', 'intent']
    }
    # evaluate whether all expected entities (label/value) are found in observed entity dict returned fby Discovery
    return test_single_case(test_dict, observed_entity_dict, resp, verbose)


def evaluate_intent(test_dict, resp):
    """
    :param test_dict: Dict
    :param resp: Dict, response returned from Discovery after posting transcript
    :return: Tuple(int, str, str)
        element 1: 0 if test passed and expected_intent is the same as observed intent else 1
        element 2: expected intent value
        element 3: observed intent value
    """
    expected_intent = test_dict["intent"]
    # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
    observed_intent = resp["intents"][0]["label"]

    failed_test = 0 if expected_intent == observed_intent else 1

    if failed_test:
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


def print_table(timing_list, top_n=5, first_k_chars=25):
    """ 
    Prints a formatted table ordered by longest test timings. 
        
    :param timing_list: namedtuple, list of namedtuples representing testing results
    """

    sorted_timing = sorted(timing_list, key=lambda tup: tup.time_dif_ms, reverse=True)
    print("\nTop", top_n, "longest timed tests:\n")
    print('{:<30s}{:<12s}{:<30s}{:<35s}{:<25s}'.format('test_file_name', 'test_no',
                                                       'test_name', 'transcript',
                                                       'time(ms)'))
    print(120 * '-')

    for x in sorted_timing[:top_n]:
        print('{:<30s}{:<12d}{:<30s}{:<35s}{:<25.2f}'.format(
            x.test_file[:first_k_chars], x.test_no, x.test_name[:first_k_chars],
            x.transcript[:first_k_chars], x.time_dif_ms))

        
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

    t1 = time.time()

    total_tests = len(tests)

    failed_tests = total_errors = total_char_errors = total_characters = 0
    y_true, y_pred = [], []
    output_dict = defaultdict(dict)

    timing_list = []
    TimingResult = namedtuple(
        "TimingResult",
        ['test_file', 'test_no', 'test_name', 'transcript', 'time_dif_ms'])

    for test_no, test_dict in enumerate(tests):
        test_name, transcript = test_dict["test"], test_dict["transcript"]

        test_start_msg = "\n  ======Test: {}======  \n".format(test_name)
        if verbose:
            print(test_start_msg)

        # Timing submit_transcript function
        test_start_time = time.time()
        resp = submit_transcript(transcript, intent_whitelist, domain_whitelist)
        test_end_time = time.time()

        time_dif_ms = 1000 * (test_end_time - test_start_time)

        # include test filename, test number, test name, transcript, and time in ms
        timing_list.append(
            TimingResult(test_file, test_no, test_name, transcript, time_dif_ms))

        # Check if a valid response was received
        if not is_valid_response(resp):
            fail_test(resp)

        if "intent" in test_dict:
            failed_test, expected_intent, observed_intent = evaluate_intent(
                test_dict, resp)
            failed_tests += failed_test
            output_dict[test_no] = dict(
                test_name=test_name,
                transcript=transcript,
                expected_intent=expected_intent,
                observed_intent=observed_intent,
                correct=(1 if expected_intent == observed_intent else 0))
            y_true.append(expected_intent)
            y_pred.append(observed_intent)

        ################################################################################################################
        # Get all values of all entities returned by discovery for a test transcript
        entity_test_res = evaluate_entities(test_dict, resp, verbose)

        output_dict[test_no]["expected_entities"] = test_dict
        output_dict[test_no]["observed_entities"] = entity_test_res[
            'observed_entity_dict']

        failed_tests += entity_test_res['failure']
        total_errors += entity_test_res['total_errors']
        total_char_errors += entity_test_res['total_char_errors']
        total_characters += entity_test_res['total_characters']

    ####################################################################################################################
    # All tests complete
    ####################################################################################################################
    time_lapsed = round(time.time() - t1, 2)
    correct_tests = total_tests - failed_tests
    accuracy = (correct_tests / total_tests) * 100

    # Prints a table of the timing results to console
    print_table(timing_list)

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
        entity_character_error_rate = 100 * (output_dict["total_character_errors"],
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
            logger.exception(
                "Error: Check path to directory: {}".format(d), exc_info=True)
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
        list(filter(lambda x: x != "any", set((i for s in domains for i in s)))))

    if flattened_domains:
        DISCOVERY_CONFIG["DISCOVERY_DOMAINS"] = flattened_domains
        print("Limiting domains to {}".format(flattened_domains))


def print_help():
    print("Test discovery usage: ")
    print(test_discovery.__doc__)
    sys.exit(0)


def validate_directory_exists(directory):
    custom_directory = join_path(abspath(directory), "custom")
    make_sure_directories_exist([directory, custom_directory])

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


def load_tests_into_list(tests):
    """
    Take either space or comma separated tests and split into a list of tests
    """
    target_tests = []
    for test in tests:
        target_tests += [
            subtest.strip()
            for subtest in (test.split(",") if isinstance(test, str) else test)
            if subtest.strip()
        ]
    return target_tests


def test_discovery(directory, *tests, shutdown=True, help=False, verbose=False):
    """
    :param directory: Path to directory containing custom/ directory
    :param shutdown: Whether to stop Discovery container after testing
    :param help: prints this help message
    :param verbose: print extra entities found
    :param tests: Comma or space separated list of file(s) containing tests
    :return: loads yaml definitions files, launches discovery, trains custom interpreters, posts each test in tests
        and saves results + computed metrics
    """
    if help:
        print_help()

    custom_directory = validate_directory_exists(directory)

    # get all definition yaml files
    for yml_file in fnmatch.filter(custom_directory, ".yaml"):
        validate_yaml(join_path(custom_directory, yml_file))

    target_tests = load_tests_into_list(tests)
    success = run_all_tests_in_directory(directory, custom_directory, target_tests,
                                         shutdown, verbose)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    Fire(test_discovery)