#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
from os.path import abspath, exists
from os.path import join as join_path

import requests

from launch_discovery import launch_discovery
from testing.discovery_config import (
    CONTAINER_NAME,
    DISCOVERY_CONFIG,
    DISCOVERY_HOST,
    DISCOVERY_PORT,
    RETRIES,
    TIMEOUT,
)

LOGGER = logging.getLogger(__name__)

DISCOVERY_URL = "http://{}:{}/process".format(DISCOVERY_HOST, DISCOVERY_PORT)
DEVELOPER_URL = "http://{}:{}/developer".format(DISCOVERY_HOST, DISCOVERY_PORT)


def check_yaml(yaml_dir):
    yamllint_output = subprocess.check_output('python3 -m yamllint {}; exit 0;'.format(yaml_dir), shell=True).decode('utf-8')
    if 'error' in yamllint_output.lower():
        raise Exception('\n\nInvalid yaml in {}, please fix the following errors:\n{}'.format(yaml_dir, yamllint_output))


def log_discovery(previous_logs=''):
    output = subprocess.run(["docker", "logs", "{}".format(CONTAINER_NAME)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    logs = (output.stderr.decode() if isinstance(output.stderr, bytes) else output.stderr).strip()
    if previous_logs:
        logs = logs.replace(previous_logs, '').strip()
    return logs


def check_discovery_status():
    """
    Checks whether Discovery is ready to receive new jobs
    """
    r = requests.get("http://{}:{}/ping".format(DISCOVERY_HOST, DISCOVERY_PORT))
    return True if r and r.status_code == 200 else False


def discovery_container_is_running():
    """
    Checks whether the discovery container is still running
    """
    if subprocess.check_output(
            "docker ps -aq -f status=exited -f name={}".format(CONTAINER_NAME),
            shell=True):
        return False
    return True


def try_discovery(attempt_number):
    try:
        check_discovery_status()
        return True
    except Exception:
        if attempt_number >= RETRIES / 4:
            LOGGER.error("Could not reach discovery, attempt {0} of {1}".format(
                attempt_number + 1, RETRIES))
        time.sleep(TIMEOUT)


def print_logs(full_logs):
    incremental_logs = log_discovery(full_logs)
    full_logs += incremental_logs
    if incremental_logs:
        print(incremental_logs)
    return full_logs


def wait_for_discovery_status():
    """
    Wait for Discovery to be ready
    """
    full_logs = ''
    for attempt_number in range(RETRIES):
        if try_discovery(attempt_number):
            return True
        full_logs = print_logs(full_logs)
        if not discovery_container_is_running():
            return False
    return False


def wait_for_discovery_launch():
    """
    Wait for launch to complete
    """
    # Timeout of 25 seconds for launch
    if not wait_for_discovery_status():
        LOGGER.error("Couldn't launch Discovery")
        shutdown_discovery()
        sys.exit(1)
    else:
        print("Discovery Launched!")


def make_sure_directories_exist(directories):
    for d in directories:
        try:
            assert exists(d)
        except AssertionError:
            LOGGER.exception("Error: Check path to directory: {}".format(d),
                             exc_info=True)
            print("Terminating program")
            sys.exit(1)


def validate_custom_directory(directory):
    custom_directory = join_path(abspath(directory), "custom")
    check_yaml(custom_directory)
    make_sure_directories_exist([directory, custom_directory])

    return custom_directory


def limit_discovery_domains(directory, domains):

    flattened_domains = ",".join(
        list(filter(lambda x: x != "any", set((i for s in domains for i in s)))))

    if flattened_domains:
        DISCOVERY_CONFIG["DISCOVERY_DOMAINS"] = flattened_domains
        print("Limiting domains to {}".format(flattened_domains))


def setup_discovery(directory, custom_directory, domains):
    limit_discovery_domains(directory, domains)
    volume = launch_discovery(custom_directory=custom_directory)
    wait_for_discovery_launch()
    return volume


def submit_transcript(transcript,
                      intent_whitelist=["any"],
                      domain_whitelist=["any"],
                      external_json=None):
    """
    Submits a transcript to Discovery
    :param transcript: str,
    :param intent_whitelist: str; 'any' (default) or list of intent labels (if intent_whitelist in test_file)
    :param domain_whitelist: str: 'any' (default) or list of domain labels (if domain_whitelist in test_file)
    """
    payload = {
        "transcript": transcript,
        "intents": intent_whitelist,
        "domains": domain_whitelist,
    }

    # merge with file json when given
    if external_json is not None:
        # having "transcript" at the top level of payload caused issues for input gk json that contain "segments"
        # nlprocessor_earnings_call_test_1.json contains a transcript in segments[0]['transcript'] and discovery output
        # was missing interpreted_fields.
        # remove the conflicting transcript key below. The other external_json tests contain "transcript" at the top, so
        # it is present and tests work
        del payload["transcript"]
        payload = {**external_json, **payload}

    response = requests.post(DISCOVERY_URL, json=payload)
    if not response.status_code == 200:
        LOGGER.error("Request was not successful. Response Status Code: {}".format(
            response.status_code))
        return {}
    return response.json()


def get_discovery_config():
    "query developer route and get intents if available"
    r = requests.get(DEVELOPER_URL)
    payload = json.loads(r.text)
    return payload


def reload_discovery_config():
    "POST to developer route to reload config"
    r = requests.post(DEVELOPER_URL)
    payload = json.loads(r.text)
    return ('result' in payload and payload['result'] == "success")


def shutdown_discovery(volume=None):
    """
    Shuts down the Discovery engine Docker container
    """
    if str(os.environ.get('SHUTDOWN_DISCOVERY', True)) == "False":
        return

    LOGGER.info("Shutting down Discovery")
    try:
        subprocess.call("docker rm -f {}".format(CONTAINER_NAME), shell=True)
    except Exception as exc:
        LOGGER.exception(exc)

    if volume is not None:
        subprocess.call("docker volume rm {}".format(volume), shell=True)
