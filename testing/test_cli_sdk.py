#!/usr/bin/env python3
"""
Exercise selected functions from cli_sdk to improve coverage
"""

import pytest

import cli_sdk

intent = "digit"
transcript = "please dial eight"
expected_response = {
    "formatted_entities": [
        {"confidence": 1.0, "length": 1.2, "start": 0.0, "word": "please"},
        {"confidence": 1.0, "length": 0.8, "start": 1.2, "word": "dial"},
        {
            "IOB": "B",
            "confidence": 1.0,
            "interpreted_transcript": "eight",
            "label": "digits",
            "length": 1.0,
            "start": 2.0,
            "word": "8",
        },
    ],
    "formatted_transcript": "please dial 8",
    "intents": [
        {
            "entities": [
                {
                    "label": "digits",
                    "matches": [
                        {
                            "endTimeSec": 3.0,
                            "interpreted_transcript": "eight",
                            "lattice_path": [[2, 0, None]],
                            "probability": 1.0,
                            "startTimeSec": 2.0,
                            "value": "8",
                        }
                    ],
                }
            ],
            "label": "digit",
            "probability": 1.0,
        }
    ],
    "transcript": "please dial eight",
}


class TestCLISDK:
    def test_get_response(self):
        "Ensures responses behave as expected"

        assert cli_sdk.get_response(intent, transcript, raw_data=False) is None
        assert (
            cli_sdk.get_response(intent, transcript, raw_data=True) == expected_response
        )

    def test_get_entities(self):
        "Ensures we can fetch entities"
        # get_entities
        cli_sdk.get_entities(intent, transcript)
        resp = cli_sdk.get_entities(intent, transcript, raw_data=True)
        assert resp.columns.tolist() == ["entity", "value", "tokens", "indices"]
        assert resp.values.tolist() == [["digits", "8", "eight", [2]]]

    def test_restart(self):
        "Ensures restarts and reloads work"
        cli_sdk.restart("examples")
        cli_sdk.reload()
        resp = cli_sdk.get_response(intent, transcript, raw_data=True)
        assert resp == expected_response

    def test_log(self):
        "Tests log fetching"
        log = cli_sdk.log()
        assert isinstance(log, str) and len(log) > 0

    def test_get_schema(self):
        "Test we can fetch keys in json responses"
        resp = cli_sdk.get_schema(intent, "test", transcript)
        assert resp == "Schema key test not found"
        cli_sdk.get_schema(intent, "intents", transcript, raw_data=False)
        resp = cli_sdk.get_schema(intent, "intents", transcript, raw_data=True)
        assert resp == expected_response["intents"]

    def test_token_coverage(self):
        "Ensures we receive token coverage back"
        # get_token_coverage test - return None since it prints
        assert cli_sdk.get_token_coverage(intent, transcript) is None

        # this returns None as it prints
        assert cli_sdk.get_tokens(intent, transcript) is None


def setup_module(module):
    """setup any state specific to the execution of the given class (which
    usually contains tests).
    """
    cli_sdk.start("examples")


def teardown_module(module):
    """teardown any state that was previously setup with a call to
    setup_class.
    """
    cli_sdk.stop()
