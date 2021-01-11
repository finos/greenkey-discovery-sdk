#!/usr/bin/env python3
"""
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests pass if the defined entities are present in the most
likely found intent.
"""
import functools
import logging
import sys

import dotenv
import requests

from freeze import freezeargs
from testing.discovery_interface import submit_discovery_transcript
from testing.evaluate_tests import evaluate_entities_and_schema, is_valid_response
from testing.nlprocessor_interface import submit_nlprocessor_transcript

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s - %(asctime)s - %(name)s :: %(message)s",
)

LOGGER = logging.getLogger(__name__)
env = dotenv.dotenv_values("client.env")

# enable LRU caching if a test transcript and arguments are duplicated
submit_nlprocessor_transcript = freezeargs(
    functools.lru_cache(maxsize=None)(submit_nlprocessor_transcript))

submit_discovery_transcript = freezeargs(
    functools.lru_cache(maxsize=None)(submit_discovery_transcript))


def format_bad_response(test_name, message, resp):
    """
    Format bad response output
    """
    return f"Test {test_name} - Failed: {message}. Response: {resp}"


def format_bad_entities(test_dict, test_results):
    """
    Format error for pytest output
    """
    expected_output = {
        k: v
        for k, v in test_dict.items() if k not in [
            "test",
            "transcript",
            "schema",
            "intent",
            "external_json",
            "predicted_intent",
        ]
    }
    msg = f"\nExpected: {expected_output}\nReceived: {test_results['observed_entity_dict']}"
    if "predicted_intent" in test_dict:
        msg += f"\nExpected intent: {test_dict['predicted_intent']}\nObserved intents:{test_results['observed_intents']}"

    return msg


def test_nlp_stack(test_dict, intents, nlp_models, test_name):
    """
    Test a single test dict with both nlprocessor and discovery
    """
    test_dict = test_dict.copy()
    _, transcript = test_dict.pop("test"), test_dict.pop("transcript")
    external_json = test_dict.get("external_json", {})

    resp = {}
    # post to nlprocessor
    if nlp_models:
        resp = submit_nlprocessor_transcript(transcript, nlp_models, external_json)
        # store nlprocessor output into external_json object
        external_json.update(resp)

    # post to discovery
    if intents:
        resp = submit_discovery_transcript(transcript, intents, external_json)

    # Check if a valid response was received
    assert is_valid_response(resp), format_bad_response("Invalid response", test_name,
                                                        resp)

    # Check entity tests
    test_results = evaluate_entities_and_schema(test_dict, resp)

    assert test_results.get("total_errors") in {0, None}, format_bad_entities(
        test_dict, test_results)


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main(sys.argv))
