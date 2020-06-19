#!/usr/bin/env python3

import glob
import itertools
import json

from os.path import join as join_path
from os.path import dirname
from testing.discovery_config import DISABLE_INTENTS_WHITELIST


def expand_wildcard_tests(directory, tests):
    """
    Expands any wildcard filenames in the list of tests

    >>> res = expand_wildcard_tests('examples/fruits', ['test*'])
    >>> sorted(res)
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
        tests = [t for t in tests if not t in wildcard_tests] + cleaned_filenames
    return tests


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


def load_test_file(test_file):
    return [_.strip() for _ in open(test_file) if _.strip() and not _.startswith("#")]


def make_test_list(test_list, test_folder):
    """
    Creates a dictionary definition the inputs and expected outputs of a tests into a list
    under the key expected_outputs
    """
    split_inds = [i for i, val in enumerate(test_list) if val.split(': ')[0] == 'test']
    split_list = [test_list[start:stop] for start, stop in zip(split_inds, split_inds[1:] + [len(test_list)])]
    test_def_dicts = []
    for test in split_list:
        t_dict = {}
        for line in test:
            # Update t_dict with information from each line
            t_dict = process_line(t_dict, line, test_folder)
        test_def_dicts += [t_dict]

    return test_def_dicts


def process_line(t_dict, line, test_folder):
    """
    Modify the dictionary, t_dict, in place because code climate thinks this is less complex
    """
    split_line = line.split(": ", maxsplit=1)
    if len(split_line) == 2:
        key, value = split_line
        t_dict = parse_test_line(t_dict, key, value, test_folder)
    else:
        print('Got a bad line, skipping:\n{}'.format(line))
    return t_dict


def parse_test_line(ret_dict, key, value, test_folder):
   """
   Modify the dictionary in place because code climate thinks this is less complex
   """
   if key not in ['test', 'external_entities', 'transcript']:
       # keys that define expected output of discovery
       ret_dict['expected_outputs'] = ret_dict.get('expected_outputs', []) + [(key, value)] 
   elif key == 'external_entities':
       ent_file = join_path(test_folder, 'external_entities', value)
       ret_dict[key] = json.load(open(ent_file, 'r'))['entities']
   else:
       # Unique keys (per test set) that are test definition parameters usually
       ret_dict[key] = value
   return ret_dict


def create_individual_tests(test_set):
   """
   Creates test definitions from a test set as dictionaries.
   Assumes 'expected_outputs' is a list of tuples defining expected outputs key value pairs
     [('schema', [SCHEMA-DICT]), ...]
   """

   test_inputs = {k: v for k, v in test_set.items() if k != 'expected_outputs'}
   test_dicts = [
       {k: v, **test_inputs}
       for k, v in test_set.get('expected_outputs', [(None, None)]) if v
   ]
   return test_dicts


def load_tests(test_file):
    """
    Loads and parses the test file
    """
    test_list = load_test_file(test_file)
    test_list, intent_whitelist, domain_whitelist = find_whitelists(test_list)
    test_directory = dirname(test_file)
    test_def_list = make_test_list(test_list, test_directory)

    tests = [create_individual_tests(test_set) for test_set in test_def_list]
    tests = list(itertools.chain.from_iterable(tests))

    return tests, intent_whitelist, domain_whitelist


def find_whitelists(test_file):
    """
    If testfile starts with any whitelists, separate them from the test file.
    """

    intents = [intent for intent in test_file if intent.startswith("intent_whitelist")]
    domains = [domain for domain in test_file if domain.startswith("domain_whitelist")]

    intent_whitelist = format_whitelist(intents[0]) if intents else ["any"]
    domain_whitelist = format_whitelist(domains[0]) if domains else ["any"]

    test_file = [line for line in test_file if not line in intents + domains]

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
    return (find_whitelists(
        load_test_file(join_path(directory, add_extension_if_missing(f))))[2]
            for f in (tests.split(",") if isinstance(tests, str) else tests))


def add_extension_if_missing(test_file):
    """
    Add .txt extension if not present
    >>> add_extension_if_missing('this')
    'this.txt'
    >>> add_extension_if_missing('that.txt')
    'that.txt'
    """
    if not test_file.endswith(".txt"):
        test_file += ".txt"
    return test_file
