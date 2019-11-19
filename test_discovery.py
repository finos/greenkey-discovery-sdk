#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
"""
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)-8s - %(asctime)s - %(name)s :: %(message)s"
)

logger = logging.getLogger(__name__)

import fnmatch
import glob
import json
import os
import subprocess
import sys
import time
import yaml
from collections import defaultdict, namedtuple
from os.path import abspath, exists, join as join_path

from fire import Fire
from testing.metrics import print_normalized_confusion_matrix

from testing.parse_tests import (
    load_tests, load_tests_into_list, report_domain_whitelists,
    add_extension_if_missing
)

from testing.evaluate_tests import (
    is_valid_response, fail_test, evaluate_entities_and_schema,
    evaluate_intent, format_intent_test_result
)

from testing.output_tests import (
    print_table, print_failures, record_results, TABLE_BAR_LENGTH
)

from testing.discovery_interface import (
    docker_log_and_stop, setup_discovery, submit_transcript,
    shutdown_discovery, validate_custom_directory
)

VERBOSE_LOGGING = False
SAVE_RESULTS = False

TimingResult = namedtuple(
    "TimingResult",
    ['test_file', 'test_no', 'test_name', 'transcript', 'time_dif_ms']
)
"""
Testing functions
"""


def test_one(test_dict, intent_whitelist, domain_whitelist):
    global VERBOSE_LOGGING
    y_true = y_pred = []
    intent_results = {'failure': 0}

    test_name, transcript = test_dict["test"], test_dict["transcript"]

    # Timing submit_transcript function
    test_start_time = time.time()
    resp = submit_transcript(transcript, intent_whitelist, domain_whitelist)
    test_end_time = time.time()

    time_dif_ms = 1000 * (test_end_time - test_start_time)

    # Check if a valid response was received
    if not is_valid_response(resp):
        fail_test(resp, "Invalid response", test_name)

    # Check intent tests
    if "intent" in test_dict:
        expected_intent, observed_intent = evaluate_intent(
            test_dict, resp, test_name
        )
        intent_results = format_intent_test_result(
            test_name, transcript, expected_intent, observed_intent
        )
        y_true = [expected_intent]
        y_pred = [observed_intent]

    # Check entity tests
    entity_results = evaluate_entities_and_schema(
        test_dict, resp, VERBOSE_LOGGING
    )

    intent_results["expected_entities"] = test_dict
    intent_results["observed_entities"] = entity_results['observed_entity_dict'
                                                         ]

    return y_true, y_pred, time_dif_ms, intent_results, entity_results


def test_all(test_file):
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
    global VERBOSE_LOGGING, SAVE_RESULTS
    print(TABLE_BAR_LENGTH * '-')
    print("Loading test file: {}".format(test_file))
    tests, intent_whitelist, domain_whitelist = load_tests(test_file)

    t1 = time.time()

    total_tests = len(tests)

    failed_tests = total_errors = total_char_errors = total_characters = 0
    y_true = []
    y_pred = []
    output_dict = defaultdict(dict)

    timing_list = []
    test_failures = []

    for test_no, test_dict in enumerate(tests):
        y_true_new, y_pred_new, time_elapsed, intent_results, entity_results = test_one(
            test_dict, intent_whitelist, domain_whitelist
        )

        y_true += y_true_new
        y_pred += y_pred_new

        # include test filename, test number, test name, transcript, and time in ms
        timing_list.append(
            TimingResult(
                test_file, test_no, test_dict["test"], test_dict["transcript"],
                time_elapsed
            )
        )

        failed_tests += entity_results['failure']
        failed_tests += intent_results['failure']

        total_errors += entity_results['total_errors']
        total_char_errors += entity_results['total_char_errors']
        total_characters += entity_results['total_characters']

        test_failures.append(entity_results['test_failures'])
        test_failures.append([intent_results.get('test_failures', None)])

        output_dict[test_no] = intent_results

    test_failures = [i for s in test_failures for i in s]
    test_failures = [_ for _ in test_failures if _]

    if test_failures:
        print_failures(test_failures)

    ####################################################################################################################
    # All tests complete
    ####################################################################################################################
    time_lapsed = round(time.time() - t1, 2)
    correct_tests = total_tests - failed_tests
    accuracy = (correct_tests / total_tests) * 100

    if y_true and y_pred:
        print_normalized_confusion_matrix(y_true, y_pred)

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

    return record_results(output_dict, VERBOSE_LOGGING, SAVE_RESULTS)


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


def print_help():
    print("Test discovery usage: ")
    print(test_discovery.__doc__)
    sys.exit(0)


def evaluate_all_tests(directory, tests):
    return all(
        test_all(join_path(directory, add_extension_if_missing(test_file))) for
        test_file in (tests.split(",") if isinstance(tests, str) else tests)
    )


def run_all_tests_in_directory(directory, custom_directory, tests, shutdown):
    success = False
    volume = None
    try:
        domains = report_domain_whitelists(directory, tests)
        volume = setup_discovery(directory, custom_directory, domains)
        success = evaluate_all_tests(directory, tests)
    except Exception:
        logger.exception(
            "Error: Check test files for formatting errors", exc_info=True
        )

    docker_log_and_stop(volume) if (
        not success and os.environ.get("OUTPUT_FAILED_LOGS", False)
    ) else shutdown_discovery(shutdown)
    return success


def expand_wildcard_tests(directory, tests):
    """
    Expands any wildcard filenames in the list of tests
    
    >>> expand_wildcard_tests('examples/fruits', ['test*'])
    ['tests.txt', 'tests_negative.txt']
    
    >>> expand_wildcard_tests('skip_this_directory', ['no_wildcards'])
    ['no_wildcards']
    """
    if any('*' in t for t in tests):
        wildcard_tests = [t for t in tests if '*' in t]
        expanded_filenames = [ \
            glob.glob(join_path(directory, add_extension_if_missing(t))) \
            for t in wildcard_tests \
        ]
        flattened_filenames = [i for s in expanded_filenames for i in s]
        cleaned_filenames = [
            p.replace(directory, '').strip("/") for p in flattened_filenames
        ]
        tests = [
            t for t in tests if not t in wildcard_tests
        ] + cleaned_filenames
    return tests


def test_discovery(
    directory, *tests, shutdown=True, help=False, verbose=False, output=False
):
    """
    :param directory: Path to directory containing custom/ directory
    :param shutdown: Whether to stop Discovery container after testing
    :param help: prints this help message
    :param verbose: enables verbose logging during testing
    :param tests: Comma or space separated list of file(s) containing tests
    :param output: creates JSON files with test result output
    :return: loads yaml definitions files, launches discovery, trains custom interpreters, posts each test in tests
        and saves results + computed metrics
    """
    global VERBOSE_LOGGING, SAVE_RESULTS

    if help:
        print_help()

    if verbose:
        logger.setLevel(logging.INFO)
        VERBOSE_LOGGING = True

    if output:
        SAVE_RESULTS = True

    custom_directory = validate_custom_directory(directory)

    tests = expand_wildcard_tests(directory, tests)

    # get all definition yaml files
    for yml_file in fnmatch.filter(custom_directory, ".yaml"):
        validate_yaml(join_path(custom_directory, yml_file))

    target_tests = load_tests_into_list(tests)
    success = run_all_tests_in_directory(
        directory, custom_directory, target_tests, shutdown
    )
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    Fire(test_discovery)
