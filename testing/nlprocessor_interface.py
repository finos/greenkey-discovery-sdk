#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
from os.path import abspath, exists
from os.path import join as join_path

import docker
import dotenv
import requests
from mock import patch
from yamllint.cli import run as yamllint

from testing.service_interface import prepare_payload

LOGGER = logging.getLogger(__name__)

env = dotenv.dotenv_values("client.env")


def log_nlprocessor():
    """
    Get logs of all containers whose name contains nlprocessor
    """
    client = docker.client.from_env()
    return "\n".join(
        [
            container.logs().decode()
            for container in client.containers.list(all=True)
            if "nlprocessor" in container.name
        ]
    )


def submit_nlprocessor_transcript(transcript, nlp_models, external_json=None):
    """
    Submits a transcript to NLProcessor
    :param transcript: str,
    :param domain: str,
    """
    if not nlp_models:
        return {}
    payload = {
        "transcript": transcript,
        "middlewareConfig": {"NLPROCESSOR": {"models": nlp_models}},
    }

    payload = prepare_payload(payload, external_json)

    address = ":".join([env["NLPROCESSOR_HOST"], env["NLPROCESSOR_PORT"]]) + "/process"
    response = requests.post(address, json=payload)
    if not response.status_code == 200:
        LOGGER.error(
            "Request was not successful. Response Status Code: {}".format(
                response.status_code
            )
        )
        return {}
    return response.json()
