#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
from os.path import abspath, isdir
from os.path import join as join_path

import docker
import dotenv
import requests
from mock import patch
from yamllint.cli import run as yamllint

from testing.service_interface import prepare_payload

LOGGER = logging.getLogger(__name__)

env = dotenv.dotenv_values("client.env")

DEVELOPER_URL = "{}:{}/developer".format(env["DISCOVERY_HOST"], env["DISCOVERY_PORT"])


def check_yaml(yaml_dir):
    """
    Run yamllint against directory container yaml
    """
    args = ["/home/matt/.local/bin/yamllint", yaml_dir]
    with patch.object(sys, "argv", args), patch("sys.exit") as exit_mock:
        yamllint()
        exit_mock.assert_called_once_with(0)


def make_sure_directories_exist(directories):
    """
    Ensure all directories in input list exist
    """
    for d in directories:
        assert isdir(d), f"{d} does not exist!"


def log_discovery():
    """
    Get logs of all containers whose name contains discovery
    """
    client = docker.client.from_env()
    return "\n".join([
        container.logs().decode() for container in client.containers.list(all=True)
        if "discovery" in container.name
    ])


def submit_discovery_transcript(transcript, intents, external_json=None):
    """
    Submits a transcript to Discovery
    :param transcript: str,
    :param intents: list of intent labels
    """
    payload = {
        "transcript": transcript,
        "intents": intents,
    }

    payload = prepare_payload(payload, external_json)
    address = ":".join([env["DISCOVERY_HOST"], env["DISCOVERY_PORT"]]) + "/process"
    response = requests.post(address, json=payload)
    if not response.status_code == 200:
        LOGGER.error("Request was not successful. Response Status Code: {}".format(
            response.status_code))
        return {}
    return response.json()


def validate_interpreter_directory(interpreter_directory):
    """
    Ensure directory exists and YAML is valid
    """
    make_sure_directories_exist([interpreter_directory])
    check_yaml(interpreter_directory)


def get_discovery_config():
    "query developer route and get intents if available"
    r = requests.get(DEVELOPER_URL)
    payload = json.loads(r.text)
    return payload


def reload_discovery_config():
    "POST to developer route to reload config"
    r = requests.post(DEVELOPER_URL, json={})
    payload = json.loads(r.text)
    return "result" in payload and payload["result"] == "success"
