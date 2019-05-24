#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
"""

import requests
import subprocess
import json
import os
import time
import glob
import sys
import editdistance
import logging
from os.path import join as join_path, dirname
from collections import defaultdict
from importlib import import_module
from discovery_sdk_utils import find_errors_in_entity_definition
from discovery_config import DISCOVERY_PORT, DISCOVERY_HOST, DISCOVERY_SHUTDOWN_SECRET
from discovery_config import CONTAINER_NAME
from discovery_config import TIMEOUT, RETRIES
from launch_discovery import launch_discovery

from asrtoolkit.clean_formatting import clean_up

from metrics import compute_counts, precision_recall_f1_accuracy

# TODO move to ini file
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(lineno)d %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

file_handler = logging.FileHandler('test_discovery.log')
file_handler.setLevel(logging.DEBUG)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

"""
Functions for handling the Discovery Docker container
"""

#TODO Remap the following Bash codes; confusing as opposite of standard Python codes
BAD_EXIT_CODE = 1
GOOD_EXIT_CODE = 0

UNFORMATTED_CHARS = set("abcdefghijklmnopqrstuvwxyz-' ")


def docker_log_and_stop():
    """
    name assigned to Docker container; modify CONTAINER_NAME in
    discovery_config.py
        defalut='discovery-dev'
    """
    subprocess.call("docker logs {}".format(CONTAINER_NAME), shell=True)
    subprocess.call("docker stop {}".format(CONTAINER_NAME), shell=True)


def check_discovery_status():
    """
    Checks whether Discovery is ready to receive new jobs
    """
    r = requests.get("http://{}:{}/status".format(DISCOVERY_HOST, DISCOVERY_PORT))
    return True if 'listening' in r.json()['message'] else False


def wait_for_discovery_status():
    """
    Wait for Discovery to be ready
    """
    for i in range(RETRIES):
        try:
            check_discovery_status()
            return True
        except Exception:
            # logger.exception("Error: Exception during status check", exc_info=True)
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
        exit(1)


def shutdown_discovery():
    """
    Shuts down the Discovery engine Docker container
    """
    try:
        requests.get(
            "http://{}:{}/shutdown?secret_key={}".format(DISCOVERY_HOST, DISCOVERY_PORT, DISCOVERY_SHUTDOWN_SECRET)
        )
    # Windows throws a ConnectionError for a request to shutdown a server which makes it looks like the test fail
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(3)


"""
Testing functions
"""


def json_dump(data, outfile, directory=None):
    if not directory:
        directory = os.getcwd()
    outfile = join_path(directory, outfile)
    json.dump(data, open(outfile, 'w+'))


def load_tests(test_file):
    """
    Loads and parses the test file
    """
    test_file = [x.rstrip() for x in open(test_file)]
    tests = []
    current_test = {}
    for line in test_file:
        key = line.split(":")[0]
        value = line.split(": ", maxsplit=1)[-1]
        if key == "test":
            if len(current_test.keys()) > 0:
                tests.append(current_test)
            current_test = {key: value}
        elif len(key) > 0:
            current_test[key] = value
    if len(current_test.keys()) > 0:
        tests.append(current_test)
    return tests


def bson_format(s):
  if s.startswith("$"):
    s = s.replace("$", "_$", 1)

  if s.endswith("."):
    s = s[:-1]

  if "." in s:
    s = s.replace(".", ",")

  return s
  
  
def generate_confusions(transcript):
    data = {"word_confusions": [{bson_format(w): "1.0"} for w in transcript.split(" ")]}
    
    i = 0
    while True:
      if i >= (len(data['word_confusions']) - 1):
        break
        
      word = list(data['word_confusions'][i].keys())[0]
      confidence = data['word_confusions'][i][word]
      
      if confidence == "1.0" and any(map(lambda c: c not in UNFORMATTED_CHARS, word)):
        additional_words = clean_up(word).split(" ")
        data['word_confusions'][i][additional_words[0]] = "0.1"
        
        if len(additional_words) > 1:
          for w in reversed(additional_words[1:]):
            data['word_confusions'].insert(i+1, {"<unk>": "0.9", w: "0.1"})
                
      i += 1
          
    return data    
      

def submit_transcript(transcript):
    """
    Submits a transcript to Discovery
    """
    data = generate_confusions(transcript)
    
    if any(map(lambda c: c not in UNFORMATTED_CHARS, transcript)):
      data['punctuated_transcript'] = transcript
      data['transcript'] = clean_up(transcript)
    else:
      data['transcript'] = transcript
    
    response = requests.post("http://{}:{}/process".format(DISCOVERY_HOST, DISCOVERY_PORT), json=data)
    if response.status_code == 200:
      return response.json()
    else:
      logger.error("Request was not successful. Response Status Code: {}".format(response.status_code))
      return {}


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
    Run a single test case and return the number of errors

    :param test_dict: dict;
	key: str; name of entity
	value: str; first occurrence of entity in transcript

    :param response_intent_dict: dict, single intent from Discovery response

    :return: 4-Tuple
        first element: bool; 0 if tests pass, 1 if tests fails
	total_errors: int; number of entities in test whose observed value (str) differs from expected
	total_char_errors: int; sum of number of char that differ between observed and expected values for each entity
        characters: int; 
    """
    # Get all values of entities
    entities = {ent["label"]: ent["matches"][0][0]["value"] for ent in response_intent_dict["entities"]}

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

    Compares expected intent and entities (from test) with discovery returned intents and entities

    :param test_file: str, test file
        each intent tested must contain the following key/value pairs:
        test: name of test
        transcript: text to send to discovery
	optionally:
	    intent: name of intent (only one label for each intent tested)
	    entity_name: text that Discovery identified as an instance of the entity
			as many entities as defined for a given intent
    :return 
        prints to stdout
	    (1) the number of tests that pass
	    (2) the time it took to run the tests
	    (3) total number of character errors in entities tested
	    (4) the entity character error rate
         saves 2 json files: 
            (1) test_results.json: contains expected intent labels and corresponding model predicted labels
            (2) test_metrics.json: computes precision, recall, f1_score and accuracy is possibe; else returns accuracy and count confusion matrix
    """
    tests = load_tests(test_file)

    t1 = int(time.time())

    total_tests = len(tests)
    failed_tests = 0
    total_errors = 0
    total_char_errors = 0
    total_characters = 0

    y_true = []
    y_pred = []

    for test in tests:
        logger.info("======\nTesting: {}".format(test['test']))

        resp = submit_transcript(test['transcript'])

        # Check if a valid response was received
        if not is_valid_response(resp):
            fail_test(resp)

        # keep only the most likely hypothesis from Discovery
        most_likely_intent = resp["intents"][0]

        if 'intent' in test:
            expected_intent, observed_intent = test['intent'], most_likely_intent['label']
            y_true.append(expected_intent)
            y_pred.append(observed_intent)
            message = "\nExpected Intent: {} \nObserved Intent{}".format(expected_intent, observed_intent)
            logger.info(message)

            if expected_intent != observed_intent:
                observed_not_expected_msg = "Observed intent does not match expected intent!"
                failed_tests += 1
                fail_test(resp, message=observed_not_expected_msg, continued=True)

        (failure, errors, char_errors, characters) = test_single_case(test, most_likely_intent)
        failed_tests += failure
        total_errors += errors
        total_char_errors += char_errors
        total_characters += characters

    time_lapsed = int(time.time()) - t1
    total_entity_character_errors = total_errors
    correct_tests = total_tests - failed_tests
    accuracy = correct_tests / total_tests

    output_dir = dirname(test_file)

    # save output variables computed across tests
    output_dict = dict(
        total_tests=total_tests,
        test_time_sec=time_lapsed,
        expected_intents=y_true,
        observed_intents=y_pred,
        total_entity_character_errors=total_errors,
        total_character_errors=total_char_errors,
        total_characters=total_characters
    )
    json_dump(data=output_dict, outfile='test_results.json', directory=output_dir)

    # record message regardless of number of entity errors
    message = "\n---\n({} / {}) tests passed in {} seconds\n".format(correct_tests, total_tests, time_lapsed)
    logger.info(message)
    print(message)

    if total_characters:
        entity_character_error_rate = 100 * (total_char_errors / total_characters)
        msg = "\nTotal number of entity character errors: {} \nEntity Character Error Rate: {}".format(
            total_entity_character_errors, "{:.2f}".format(entity_character_error_rate)
        )
        logger.info(msg)

    # evaluate metrics; treat each possible intent as the reference label
    # (key=label; value=dict with performance metrics)
    metrics_dict = defaultdict(dict)
    metrics_dict['accuracy_score'] = accuracy * 100
    intent_labels = set(y_true)
    for label in intent_labels:
        try:
            metrics = precision_recall_f1_accuracy(y_true, y_pred, label=label)
            # del metrics['accuracy']  # -> Dict
        except ZeroDivisionError:
            metrics = compute_counts(y_true, y_pred, label=label)
        metrics_dict[label] = metrics
    json_dump(metrics_dict, outfile='test_metrics.json', directory=output_dir)

    # total_errors
    if total_entity_character_errors > 0:
        logger.error(
            "\nTotal entity characters found: {}\nShutting down Discovery\n".format(total_entity_character_errors)
        )
        shutdown_discovery()
        exit(1)


def fail_test(resp, message="", continued=False):
    print("Test failed: " + message)
    print("{}\n---\n".format(resp))

    if not continued:
        docker_log_and_stop()
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
    if len(sys.argv) > 1:
        DISCOVERY_DIRECTORY = os.path.abspath(sys.argv[1])
    else:
        DISCOVERY_DIRECTORY = os.getcwd()

    TEST_FILE = os.path.join(DISCOVERY_DIRECTORY, "tests.txt")

    validate_entities(DISCOVERY_DIRECTORY)
    validate_json(DISCOVERY_DIRECTORY)
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
