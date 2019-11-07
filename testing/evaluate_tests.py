#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

import editdistance
import json

from testing.format_tests import strip_extra_whitespace
"""
Helper functions
"""


def fail_test(resp, message="", test_name=''):
    logger.info("Test {0} - Failed: {1}".format(test_name, message))


def request_failed(resp):
    return "result" in resp and resp["result"] == "failure"


def missing_intent_or_entity(resp):
    return not ("intents" in resp and resp["intents"] and resp["intents"][0])


def is_valid_response(resp):
    """
    Validates a Discovery response
    Fail if a failure response was received
    """
    return False if request_failed(resp) or missing_intent_or_entity(
        resp
    ) else True


"""
Schema tests
"""


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


def test_schema(full_response, test_value, test_name=''):
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
        logger.info(
            "Test {0} - Schema test failed for {1} with response {2}".format(
                test_name, test_value, errs
            )
        )
        logger.info(
            "Test {0} - Full response is {1}".format(test_name, full_response)
        )

    return len(errs), json.dumps(errs)


"""
Entity tests
"""


def test_single_entity(entities, entity_label, test_value, test_name=''):
    """
    Tests a single entity within a test case
    :param entities:
    :param entity_label:
    :param test_value: str, expected substrings for
    :param test_name: str
    """
    if entity_label not in entities.keys():
        logger.info(
            "Test {0} - Entity not found: {1}".format(test_name, entity_label)
        )
        return 1, len(test_value), '[value missing]'

    if entities[entity_label] != test_value:
        logger.info(
            "Test {0} - Observed Entity Value Incorrect: ({1}) Expected {2} != {3}"
            .format(
                test_name, entity_label, test_value, entities[entity_label]
            )
        )
        return 1, editdistance.eval(test_value, entities[entity_label]
                                    ), entities[entity_label]
    return 0, 0, ''


def print_extra_entities(observed_entity_dict, test_dict, test_name=''):
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
        logger.info(
            "Test {0} - Extra entities: {1}".format(test_name, extra_entities)
        )


"""
Intent tests      
"""


def evaluate_intent(test_dict, resp, test_name=''):
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
        logger.info(
            "Test {0} - Observed intent {1} does not match expected intent {2}"
            .format(test_name, observed_intent, expected_intent)
        )

    return expected_intent, observed_intent


def format_intent_test_result(
    test_name, transcript, expected_intent, observed_intent
):
    return dict(
        test_name=test_name,
        transcript=transcript,
        expected_intent=expected_intent,
        observed_intent=observed_intent,
        failure=(1 if expected_intent != observed_intent else 0),
        test_failures=(
            [test_name, 'intent', expected_intent, observed_intent]
            if expected_intent != observed_intent else []
        )
    )


"""
Evaluate entity and schema tests    
"""


def run_test_dict(
    full_response,
    observed_entity_dict,
    entity_label,
    expected_entity_value,
    test_name=''
):
    char_errors = 0
    if entity_label == "schema":
        errors, error_value = test_schema(
            full_response, json.loads(expected_entity_value), test_name
        )
    else:
        errors, char_errors, error_value = test_single_entity(
            observed_entity_dict, entity_label, expected_entity_value,
            test_name
        )
    return errors, char_errors, len(expected_entity_value), error_value


def test_single_case(test_dict, observed_entity_dict, full_response, test_name=''):
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

    test_failures = []

    # Loop through all entity tests
    for label, value in test_dict.items():
        entity_label, expected_entity_value = map(
            strip_extra_whitespace, [label, value]
        )
        full_response = strip_extra_whitespace(full_response)

        errors, char_errors, characters, error_value = run_test_dict(
            full_response, observed_entity_dict, entity_label,
            expected_entity_value, test_name
        )

        if errors:
            test_failures.append(
                [
                    test_name, entity_label, expected_entity_value,
                    error_value
                ]
            )

        total_errors += errors
        total_char_errors += char_errors
        total_characters += len(expected_entity_value)

    print_extra_entities(observed_entity_dict, test_dict, test_name)

    return dict(
        failure=(1 if total_errors else 0),
        total_errors=total_errors,
        total_char_errors=total_char_errors,
        total_characters=total_characters,
        observed_entity_dict=observed_entity_dict,
        test_failures=test_failures
    )


def evaluate_entities_and_schema(
    test_dict, resp, verbose=False, num_intents=0
):
    """
    :param test_dict: Dict, single test case (line in test file)
    :param resp: Dict, jsonified requests.Response object returned from Discovery
    :return: 4-Tuple, see test_single_test_case
        for a given test, tests whether each entity in test is present in
            response entities dict and, if so, whether observed value matches expected value
    """
    if verbose:
        logger.setLevel(logging.INFO)

    if resp["intents"]:
        entities = most_likely_entities = resp["intents"][num_intents]["entities"]
        observed_entity_dict = {
            # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
            ent["label"]: ent["matches"][0]["value"]
            for ent in entities  #most_likely_entities
        }
    else:
        observed_entity_dict = {}
    
    test_name = test_dict.get('test', '')
    
    # Remove non-entity keys from test_dict, then pass to `test_single_case`
    test_dict = {
        k: v
        for k, v in test_dict.items() if not k in ['transcript', 'intent', 'test']
    }
    # evaluate whether all expected entities (label/value) are found in observed entity dict returned fby Discovery
    return test_single_case(test_dict, observed_entity_dict, resp, test_name)
