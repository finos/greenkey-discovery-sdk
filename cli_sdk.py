#!/usr/bin/env python3
"""
Command line interface for launching SDK and getting responses
"""

import json
import os

from interactive_sdk import format_entities, get_entities_from_discovery
from launch import launch_docker_compose, teardown_docker_compose
from testing.discovery_interface import (
    log_discovery,
    reload_discovery_config,
    submit_discovery_transcript,
    validate_interpreter_directory,
)


def start(interpreter_directory=os.environ.get("INTERPRETER_DIRECTORY",
                                               "examples/calling_room")):
    """
    Start discovery with interpreter defined by environment variable INTERPRETER_DIRECTORY.
    """
    validate_interpreter_directory(interpreter_directory)
    launch_docker_compose("discovery", interpreter_directory)


def stop():
    """
    Stop discovery
    """
    teardown_docker_compose()


def reload():
    """
    Reload discovery config
    """
    reload_discovery_config()


def restart(interpreter_directory=os.environ.get("INTERPRETER_DIRECTORY",
                                                 "examples/calling_room")):
    """
    Restart discovery with interpreter defined by environment variable INTERPRETER_DIRECTORY.
    default is "examples/calling_room"
    """
    stop()
    start(interpreter_directory)


def log():
    """
    Get all discovery logs
    """
    return log_discovery()


def return_json_data(data, raw=False):
    """
    If raw: return data; else: print it
    """
    if raw:
        return data
    print(json.dumps(data, sort_keys=True, indent=2))


def get_schema(intent, schema_key, transcript, raw_data=False):
    """
    Get a specific key from output
    """
    payload = submit_discovery_transcript(transcript, [intent])
    if schema_key in payload:
        return return_json_data(payload[schema_key], raw_data)
    else:
        return "Schema key {} not found".format(schema_key)


def get_response(intent, transcript, raw_data=False):
    """
    Get json response from discovery
    """
    payload = submit_discovery_transcript(transcript, [intent])
    return return_json_data(payload, raw_data)


def get_entities(intent, transcript):
    """
    Load entities discovered
    """
    payload = submit_discovery_transcript(transcript, [intent])
    entities = get_entities_from_discovery(payload)
    config = {"entities": [entity["label"] for entity in entities]}
    print(format_entities(entities, config))


def get_token_logs(intent, transcript):
    """
    Get tokenization report from discovery logs
    """
    submit_discovery_transcript(transcript, [intent])
    logs = log_discovery().splitlines()
    output = []
    separators = 0
    for line in reversed(logs):
        separators += line.startswith("===")
        if separators > 0:
            output.append(line)
        if separators == 2:
            break
    return reversed(output)


def get_tokens(intent, transcript):
    """
    Print tokens
    """
    print("\n".join(get_token_logs(intent, transcript)))


def get_token_coverage(intent, transcript):
    """
    Show what parts of the transcript were recognized
    """
    token_lines = list(get_token_logs(intent, transcript))[3:-1]
    tokens = [[w for w in t.split(" ") if w][-2:] for t in token_lines]
    transcript = [w[-1] for w in tokens]
    coverage = [("*" if w[0] != "None" else " ") * len(w[-1]) for w in tokens]
    print("""
    Recognized parts of the transcript are denoted with '*'

    {0}
    {1}
    """.format(" ".join(transcript), " ".join(coverage)))
