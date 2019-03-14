#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
"""

from __future__ import print_function
import requests
import subprocess
import json
import os
import time
import glob
import sys
import editdistance

from importlib import import_module
from discovery_sdk_utils import find_errors_in_entity_definition
from discovery_config import DISCOVERY_PORT, DISCOVERY_HOST, DISCOVERY_SHUTDOWN_SECRET
from launch_discovery import launch_discovery

"""
Functions for handling the Discovery Docker container
"""


def check_discovery_status():
    """
    Checks whether Discovery is ready to receive new jobs
    """
    r = requests.get("http://{}:{}/status".format(DISCOVERY_HOST, DISCOVERY_PORT))

    if 'listening' in json.loads(r.text)['message']:
        return True

    return False


def wait_for_discovery_status(timeout=1, retries=5):
    """
    Wait for Discovery to be ready
    """
    for i in range(retries):
        try:
            check_discovery_status()
            return True
        except Exception:
            time.sleep(timeout)

    return False


def wait_for_discovery_launch():
    """
    Wait for launch to complete
    """

    # Timeout of 25 seconds for launch
    if not wait_for_discovery_status(timeout=5, retries=5):
        print("Couldn't launch Discovery, printing Docker logs:\n---\n")
        subprocess.call("docker logs discovery-dev", shell=True)
        subprocess.call("docker stop discovery-dev", shell=True)
        exit(1)


def shutdown_discovery():
    """
    Shuts down the Discovery engine Docker container
    """
    try:
        requests.get("http://{}:{}/shutdown?secret_key={}".format(DISCOVERY_HOST, DISCOVERY_PORT, DISCOVERY_SHUTDOWN_SECRET))
    # Windows throws a ConnectionError for a request to shutdown a server which makes it looks like the test fail
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(3)


"""
Testing functions
"""


def load_tests(test_file_argument):
    """
    Loads and parses the test file
    """
    test_file = [x.rstrip() for x in open(test_file_argument)]

    tests = []
    current_test = {}
    for line in test_file:
        key = line.split(":")[0]
        value = line.split(": ")[-1]
        if key == "test":
            if len(current_test.keys()) > 0:
                tests.append(current_test)
            current_test = {key: value}
        elif len(key) > 0:
            current_test[key] = value

    if len(current_test.keys()) > 0:
        tests.append(current_test)

    return tests


def submit_transcript(transcript):
    """
    Submits a transcript to Discovery
    """
    data = {"transcript": transcript}
    response = requests.post("http://{}:{}/process".format(DISCOVERY_HOST, DISCOVERY_PORT), json=data)

    return json.loads(response.text)


def is_valid_response(resp):
    """
    Validates a Discovery response
    Fail if a failure response was received
    """
    if "result" in resp and resp['result'] == "failure":
        return False

    if "intents" not in resp:
        return False

    if not resp['intents']:
        return False

    if "entities" not in resp["intents"][0]:
        return False

    return True


def test_single_entity(entities, test_name, test_value):
    """
    Tests a single entity within a test case
    """

    if test_name not in entities.keys():
        fail_test({}, "Entity not found: {}".format(test_name), continued=True)
        return (1, len(test_value))

    if entities[test_name] != test_value:
        fail_test(
            {},
            "Value incorrect: ({}) expected {} != {}".format(test_name, test_value, entities[test_name]),
            continued=True
        )
        return (1, editdistance.eval(test_value, entities[test_name]))

    return (0, 0)


def test_single_case(test_dict, response_intent_dict):
    """
    Run a single test case
    Return the number of errors

    :param test_dict: dict;
        key: str; name of entity
        value: str; first occurrence of entity in transcript

    :param response_intent_dict: dict, single intent from Discovery response

    :return: 4-Tuple
       first: 0 if tests pass, 1 if tests fails

       total_errors: number of entities in test whose observed value (str) differs from expected

       total_char_errors: sum of number of char that differ between observed and expected values for each entity

       characters:
    """
    # Get all values of entities
    entities = {ent["label"]: ent["matches"][0][0]["value"]
                for ent in response_intent_dict["entities"]}

    total_errors = 0
    total_char_errors = 0
    characters = 0

    # Loop through all entity tests
    for test_name, test_value in test_dict.items():
        if test_name in ['test', 'transcript', 'intent']:
            continue

        (errors, char_errors) = test_single_entity(entities, test_name, test_value)
        total_errors += errors
        total_char_errors += char_errors
        characters += len(test_value)

    extra_entities = {x: entities[x] for x in entities.keys() if x not in test_dict}

    if len(extra_entities) > 0:
        print("Extra entities: {}\n".format(extra_entities))

    if total_errors > 0:
        return 1, total_errors, total_char_errors, characters
    else:
        print("Test passed\n---\n")
        return 0, 0, 0, characters


def test_all(test_file):
    """
    Runs all defined tests

    Compares expected intent and entities (from test)
    with discovery returned intents and entities

    :param test_file: str, test file
        each intent tested must contain the following key/value pairs:
            test: name of test
            transcript: text to send to discovery
        optionally:
            intent: name of intent (only one label for each intent tested)
            entity_name: text that Discovery identified as an instance of the entity
                as many entities as defined for a given intent
    :return prints to stdout
        (1) the number of tests that pass
        (2) the time it took to run the tests
        (3) total number of character errors in entities tested
        (4) the entity character error rate
    """
    tests = load_tests(test_file)

    t1 = int(time.time())

    total_tests = len(tests)
    failed_tests = 0
    total_errors = 0
    total_char_errors = 0
    total_characters = 0

    for test in tests:
        print("======\nTesting: {}".format(test['test']))

        resp = submit_transcript(test['transcript'])

        # Check if a valid response was received
        if not is_valid_response(resp):
            fail_test(resp)

        # keep only the most likely hypothesis from Discovery
        most_likely_intent = resp["intents"][0]

        if 'intent' in test:
            print(
                "\n Expected Intent: {} \n Observed Intent: {}\n".format(
                    test['intent'], most_likely_intent['label']
                )
            )

        if 'intent' in test and test['intent'] != most_likely_intent['label']:
            failed_tests += 1
            fail_test(resp, message="Observed intent does not match expected intent!", continued=True)
            continue

        (failure, errors, char_errors, characters) = test_single_case(test, most_likely_intent)
        failed_tests += failure
        total_errors += errors
        total_char_errors += char_errors
        total_characters += characters

    if total_characters:
        print(
            "\n---\n({} / {}) tests passed in {}s with {} entity character errors, Entity character error rate: {}%".format(
                total_tests - failed_tests, total_tests,
                int(time.time()) - t1, total_errors,
                "{:.2f}".format((total_char_errors / total_characters) * 100)
            )
        )
    else:
        print(
             "\n---\n({} / {}) tests passed in {}s".format(
                total_tests - failed_tests, total_tests,
                int(time.time()) - t1
            )
        )
    if total_errors > 0:
        shutdown_discovery()
        exit(1)


def fail_test(resp, message="", continued=False):
    print("Test failed: " + message)
    print("{}\n---\n".format(resp))

    if not continued:
        subprocess.call("docker logs discovery-dev", shell=True)
        subprocess.call("docker stop discovery-dev", shell=True)
        exit(1)


"""
Interpreter validation
"""


class cleanText(object):
    """Mock up a module that is imported by entities so they can be imported and inspected."""
    @staticmethod
    def text2int(word_list):
        return word_list


def validate_entities(discovery_directory):
    """
    Validate entities
    """
    # mock up nlp.cleanText so that entities can be imported
    sys.modules['nlp.cleanText'] = cleanText()

    entities_file = os.path.join(discovery_directory, 'custom', 'entities')
    entities = glob.glob(os.path.join(entities_file, '*.py'))
    entities_directory = os.path.join(discovery_directory, 'custom', 'entities')
    sys.path.append(entities_directory)

    for entity in entities:
        if '__init__' in entity:
            continue
        _validate_individual_entity(entity)
        try:
            os.remove(entity.replace(".py", ".pyc"))
        except FileNotFoundError:
            pass

    # remove mocked up dummy module from modules
    sys.modules.pop('nlp.cleanText')


def _validate_individual_entity(entity):
    entity_name = os.path.split(entity)[-1].replace(".py", "")
    entity_module = import_module(entity_name)
    definition_errors = []
    if 'ENTITY_DEFINITION' in dir(entity_module):
        print('Checking entity definition {0:.<35}'.format(entity_name), end='')
        errors = find_errors_in_entity_definition(entity_module.ENTITY_DEFINITION)
        _log_entity_definition_error_results(errors)
        definition_errors.extend(errors)
    if definition_errors:
        raise Exception('Please fix all entity definition errors before running discovery!')


def _log_entity_definition_error_results(errors):
    if errors:
        print('Error! \nThe following problems were found with your entity_definition:')
        for error in errors:
            print(error)
    else:
        print('No errors!')


def validate_json(discovery_directory):
    """
    Validate intents.json
    """
    intents_config_file = os.path.join(discovery_directory, 'custom', 'intents.json')
    try:
        json.loads(''.join([x.rstrip() for x in open(intents_config_file)]))
    except Exception as e:
        print("Invalid intents.json")
        print("Error: {}".format(e))
        exit(1)
    return True


if __name__ == '__main__':
    # if len(sys.argv) > 1:
    DISCOVERY_DIRECTORY = os.getcwd()  # typically given: examples/{project_directory}
    infile = "tests.txt"  # default filename: DISCOVERY_DIRECTORY/tests.txt

    # to specify project directory and name of file with tests
    # python test_discovery.py examples/fruits tests_sample.txt
    try:
        DISCOVERY_DIRECTORY = os.path.abspath(sys.argv[1])   # project directory
    except IndexError:
        DISCOVERY_DIRECTORY = os.getcwd()
    try:
        infile = sys.argv[2]  # "tests_complete.txt" vs "tests_sample.txt"; select one as defalt
    except IndexError:
        infile = "tests.txt"

    TEST_FILE = os.path.join(DISCOVERY_DIRECTORY, infile)

    # validation
    validate_entities(DISCOVERY_DIRECTORY)
    validate_json(DISCOVERY_DIRECTORY)

    # DISCOVERY_DIRECTORY project name; contains tests.txt & directory 'custom'
    # DISCOVERY_DIRECTORY/custom/intents.json (and/or schema.json and/or entities/ directory)
    custom_directory = os.path.join(DISCOVERY_DIRECTORY, 'custom')
    try:
        launch_discovery(custom_directory=custom_directory)
        wait_for_discovery_launch()

        if wait_for_discovery_status():
            print("Discovery Ready")

        test_all(TEST_FILE)
    except Exception as e:
        shutdown_discovery()
        raise e

    shutdown_discovery()
