#!/usr/bin/env python3

import glob

from os.path import abspath, exists, join as join_path
from testing.discovery_config import DISABLE_INTENTS_WHITELIST


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


def load_tests_into_list(tests):
    """
    Take either space or comma separated tests and split into a list of tests
    """
    target_tests = []
    for test in tests:
        target_tests += [
            subtest.strip() for subtest in
            (test.split(",") if isinstance(test, str) else test)
            if subtest.strip()
        ]
    return target_tests


def store_previous_test(tests, current_test):
    if current_test and set(current_test.keys()
                            ) != set(['test', 'transcript']):
        tests.append(current_test)
    return tests


def parse_test_line(line, tests, current_test):
    key, value = line.split(": ", maxsplit=1)
    if key == "test":
        tests = store_previous_test(tests, current_test)
        current_test = {key: value}
    elif key == "schema":
        # Since we can have more than one schema test,
        # store the test so that the current_test is still available
        # to add to the new tests
        current_test[key] = value
        tests = store_previous_test(tests, current_test)
        current_test = {
            'test': current_test['test'],
            'transcript': current_test['transcript']
        }
    elif key:
        current_test[key] = value
    return tests, current_test


def load_test_file(test_file):
    return [
        _.strip() for _ in open(test_file)
        if _.strip() and not _.startswith("#")
    ]


def load_tests(test_file):
    """
    Loads and parses the test file
    """
    test_file = load_test_file(test_file)
    test_file, intent_whitelist, domain_whitelist = find_whitelists(test_file)

    tests = []
    current_test = {}
    for line in test_file:
        try:
            tests, current_test = parse_test_line(line, tests, current_test)
        except ValueError:
            continue

    tests = store_previous_test(tests, current_test)
    return tests, intent_whitelist, domain_whitelist


def find_whitelists(test_file):
    """
    If testfile starts with any whitelists, separate them from the test file.
    """

    intents = [intent for intent in test_file if intent.startswith("intent_whitelist")]
    domains = [d for d in test_file if d.startswith("domain_whitelist")]

    intent_whitelist = format_whitelist(intents[0]) if intents else ["any"]
    domain_whitelist = format_whitelist(domains[0]) if domains else ["any"]

    test_file = [l for l in test_file if l not in intents + domains]

    if DISABLE_INTENTS_WHITELIST:
        intent_whitelist = ["any"]

    return test_file, intent_whitelist, domain_whitelist


def format_whitelist(line):
    """
    Ensure whitelist is a list if it contains commas.
    """
    _, whitelist = line.split(":", maxsplit=1)

    if "," in whitelist:
        whitelist = [_.strip() for _ in whitelist.split(",")]
    else:
        whitelist = [whitelist.strip()]
    return whitelist


def report_domain_whitelists(directory, tests):
    return (
        find_whitelists(
            load_test_file(join_path(directory, add_extension_if_missing(f)))
        )[2] for f in (tests.split(",") if isinstance(tests, str) else tests)
    )


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
