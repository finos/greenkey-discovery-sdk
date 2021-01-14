#!/usr/bin/env python3

import logging

logger = logging.getLogger(__name__)

import json
from datetime import date

from testing.format_tests import strip_extra_whitespace
"""
Helper functions
"""


def is_valid_response(resp):
    """
    Validates a Discovery response
    Fail if a failure response was received
    """
    return resp.get("result") != "failure"


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
    for _, v in obj.items():
        item = _find(v, key)
        if item is not None:
            return item


def _find(obj, key):
    if isinstance(obj, list):
        return _find_in_list(obj, key)
    if isinstance(obj, dict):
        return _find_in_dict(obj, key)


def is_invalid_schema(schema, test_value):
    """
    Checks schema against tests with dictionary nesting

    >>> is_invalid_schema({"valid_key": "some_value"}, {"valid_key": "some_value"})
    False

    >>> is_invalid_schema({"invalid_key": "some_value"}, {"valid_key": "some_value"})
    True

    >>> is_invalid_schema(
    ... {"nested": {"valid_key": "some_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    False

    >>> is_invalid_schema(
    ... {"nested": {"invalid_key": "some_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    True

    >>> is_invalid_schema(
    ... {"nested": {"valid_key": "some_invalid_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    True

    >>> is_invalid_schema(
    ... {"nested": {"double": {"valid_key": "some_value", "another_key": "some_value"}}},
    ... {"nested": {"double": {"valid_key": "some_value"}}}
    ... )
    False

    >>> is_invalid_schema(
    ... {"nested": {"double": {"valid_key": "some_value", "another_key": "some_value"}}},
    ... {"nested": {"double": {"valid_key": "some_value"}, "some_key": "no_value"}}
    ... )
    True
    """
    if isinstance(test_value, dict):
        return any(
            is_invalid_schema(schema[k], test_value[k]) if k in schema else True
            for k in test_value.keys())
    return schema != test_value


def test_schema(resp, test_value, test_name=""):
    """
    For each key-value pair given in the schema test,
    recursively search the JSON response for the key,
    then make sure the value is correct
    """

    # Returning number of errors, so check for values that do not equal test case
    errs = {}
    for res in map(
            lambda k: {k: _find(resp, k)}
            if is_invalid_schema(_find(resp, k), test_value[k]) else {},
            list(test_value.keys()),
    ):
        errs.update(res)

    if errs:
        logger.info("Test {0} - Schema test failed for {1} with response {2}".format(
            test_name, test_value, errs))
        logger.info("Test {0} - Full response is {1}".format(test_name, resp))

    return len(errs), json.dumps(errs)


"""
Entity tests
"""


def test_single_entity(entities, entity_label, test_value, test_name=""):
    """
    Tests a single entity within a test case
    :param entities:
    :param entity_label:
    :param test_value: str, expected substrings for
    :param test_name: str
    """
    if entity_label not in entities.keys():
        logger.info("Test {0} - Entity not found: {1}".format(test_name, entity_label))
        return 1, "[value missing]"

    if entities[entity_label] != test_value:
        logger.info(
            "Test {0} - Observed Entity Value Incorrect: ({1}) Expected {2} != {3}".
            format(test_name, entity_label, test_value, entities[entity_label]))
        return 1, entities[entity_label]

    return 0, ""


def print_extra_entities(observed_entity_dict, test_dict, test_name=""):
    """prints entities found by discovery but not specified in test file
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
        logger.info("Test {0} - Extra entities: {1}".format(test_name, extra_entities))


"""
Intent tests
"""


def evaluate_intent(test_dict, resp, test_name=""):
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
            "Test {0} - Observed intent {1} does not match expected intent {2}".format(
                test_name, observed_intent, expected_intent))

    return expected_intent, observed_intent


def format_intent_test_result(test_name, expected_intent, observed_intent):
    return dict(
        expected_intent=expected_intent,
        observed_intent=observed_intent,
        test_failures=([test_name, "intent", expected_intent, observed_intent]
                       if expected_intent != observed_intent else []),
    )


"""
Evaluate entity and schema tests
"""


def get_observed_values(resp):
    """
    Get observed values from response
    """
    # get ents from first (and only) intent
    entities = resp["intents"][0].get("entities", []) if resp.get("intents") else []

    observed_entity_dict = {}
    # add nlprocessor entities from formatted_entities
    for entity in resp.get("formatted_entities", []):
        if entity.get("label", "") not in {"O", ""}:
            label = entity["label"].replace("B-", "").replace("I-", "")
            observed_entity_dict[label] = strip_extra_whitespace(
                observed_entity_dict.get(label, "") + " " + entity.get("word"))

    observed_entity_dict = {
        **observed_entity_dict,
        **{
            # keep only the most likely hypothesis from Discovery -> first dict in list of dicts returned by Discovery
            ent["label"]: ent["matches"][0]["value"]
            for ent in entities
        },
    }

    # store predicted intent
    observed_intents = [intent["label"] for intent in resp.get("intents", [])]
    return observed_entity_dict, observed_intents


def check_entities(test_dict, resp, test_name, observed_entity_dict):
    """
    Check entities against expected results
    """
    results = []
    total_errors = 0
    # Loop through all entity tests
    for label, value in test_dict.items():
        entity_label, expected_entity_value, resp = map(strip_extra_whitespace,
                                                        [label, value, resp])

        if entity_label == "schema":
            errors, error_value = test_schema(resp, json.loads(expected_entity_value),
                                              test_name)
        elif entity_label == "predicted_intent":
            continue
        else:
            errors, error_value = test_single_entity(observed_entity_dict, entity_label,
                                                     expected_entity_value, test_name)

        results.append(
            [errors, test_name, entity_label, expected_entity_value, error_value])

        total_errors += errors

    # Only keep test failures
    test_failures = [r[1:] for r in results if r[0]]

    return test_failures, total_errors


def check_intents(test_dict, observed_intents):
    """
    Check intents
    """
    total_errors = 0
    if (test_dict.get("predicted_intent")
            and test_dict["predicted_intent"] not in observed_intents):
        total_errors += 1
    return total_errors


def test_single_case(test_dict, resp, test_name=""):
    """
    Run a single test case and return the number of errors

    :param test_dict: dict;
        keys: str; name of entity
        values: str; first occurrence of entity in transcript
    :return: Tuple(bool, int, int, int)
        first element: bool; 0 if tests pass, 1 if tests fails
        total_errors: int; number of entities in test whose observed value (str) differs from expected
        total_entities: int; sum of number of entities (including schema tests)
    """
    total_errors = 0

    observed_entity_dict, observed_intents = get_observed_values(resp)

    new_errors = check_intents(test_dict, observed_intents)
    total_errors += new_errors

    test_failures, new_errors = check_entities(test_dict, resp, test_name,
                                               observed_entity_dict)
    total_errors += new_errors

    print_extra_entities(observed_entity_dict, test_dict, test_name)

    return dict(
        total_errors=total_errors,
        observed_entity_dict=observed_entity_dict,
        observed_intents=observed_intents,
        test_failures=test_failures,
    )


def evaluate_entities_and_schema(test_dict, resp):
    """
    :param test_dict: Dict, single test case (line in test file)
    :param resp: Dict, jsonified requests.Response object returned from Discovery
    :param intent: Int, index of intent to test
    :return: 4-Tuple, see test_single_test_case
        for a given test, tests whether each entity in test is present in
            response entities dict and, if so, whether observed value matches expected value
    """

    test_name = test_dict.get("test", "Unnamed Test")

    # Remove non-entity keys from test_dict, then pass to `test_single_case`
    test_dict = {
        k: v.replace("@CUR_2DIGIT_YEAR",
                     str(date.today().year)[-2:])
        for k, v in test_dict.items()
        if k not in ["transcript", "intent", "test", "external_json"]
    }
    # evaluate whether all expected entities (label/value) are found in observed entity dict returned fby Discovery
    return test_single_case(test_dict, resp, test_name)
