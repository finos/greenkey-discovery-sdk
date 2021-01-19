#!/usr/bin/env python3

"""
ensure that cli_sdk routes are tested
"""
import cli_sdk


def test_cli_sdk():
    """
    Exercise selected functions from cli_sdk to improve coverage
    """
    cli_sdk.start("examples/digit/custom")
    resp = cli_sdk.get_response("digit", "please dial eight", raw_data=True)
    expected_response = {
        "transcript": "please dial eight",
        "intents": [
            {
                "label": "digit",
                "probability": 1.0,
                "entities": [
                    {
                        "label": "room_number",
                        "matches": [
                            {
                                "value": "8",
                                "probability": 1.0,
                                "lattice_path": [[2, 0, None]],
                                "startTimeSec": 2.0,
                                "endTimeSec": 3.0,
                                "interpreted_transcript": "eight",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    assert resp == expected_response
    cli_sdk.restart("examples/digit/custom")
    cli_sdk.reload()
    resp = cli_sdk.get_response("digit", "please dial eight", raw_data=True)
    assert resp == expected_response

    cli_sdk.get_token_coverage("digit", "please dial eight")
    cli_sdk.stop()
