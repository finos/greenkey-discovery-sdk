#!/usr/bin/env python3

import logging
LOGGER = logging.getLogger(__name__)

import json
import requests
import subprocess
import sys
import time

from os.path import abspath, exists, join as join_path

from testing.discovery_config import (
    CONTAINER_NAME,
    DISCOVERY_CONFIG,
    DISCOVERY_HOST,
    DISCOVERY_PORT,
    RETRIES,
    TIMEOUT,
)

from launch_discovery import launch_discovery

DISCOVERY_URL = "http://{}:{}/process".format(DISCOVERY_HOST, DISCOVERY_PORT)
DEVELOPER_URL = "http://{}:{}/developer".format(DISCOVERY_HOST, DISCOVERY_PORT)


def docker_log_and_stop(volume=None):
    """
    name assigned to Docker container; modify CONTAINER_NAME in
    discovery_config.py
        default='discovery-dev'
    """
    subprocess.call("docker logs {}".format(CONTAINER_NAME), shell=True)
    subprocess.call("docker stop {}".format(CONTAINER_NAME), shell=True)
    if volume is not None:
        subprocess.call("docker volume rm {}".format(volume), shell=True)


def check_discovery_status():
    """
    Checks whether Discovery is ready to receive new jobs
    """
    r = requests.get(
        "http://{}:{}/status".format(DISCOVERY_HOST, DISCOVERY_PORT)
    )
    return True if "listening" in r.json()["message"] else False


def try_discovery(attempt_number):
    try:
        check_discovery_status()
        return True
    except Exception:
        if attempt_number >= 3:
            LOGGER.error(
                "Could not reach discovery, attempt {0} of {1}".format(
                    attempt_number + 1, RETRIES
                )
            )
        time.sleep(TIMEOUT)


def wait_for_discovery_status():
    """
    Wait for Discovery to be ready
    """
    for attempt_number in range(RETRIES):
        if try_discovery(attempt_number):
            return True
    return False


def wait_for_discovery_launch():
    """
    Wait for launch to complete
    """
    # Timeout of 25 seconds for launch
    if not wait_for_discovery_status():
        LOGGER.error("Couldn't launch Discovery, printing Docker logs:\n---\n")
        docker_log_and_stop()
        sys.exit(1)
    else:
        print("Discovery Launched!")


def make_sure_directories_exist(directories):
    for d in directories:
        try:
            assert exists(d)
        except AssertionError:
            LOGGER.exception(
                "Error: Check path to directory: {}".format(d), exc_info=True
            )
            print("Terminating program")
            sys.exit(1)


def validate_custom_directory(directory):
    custom_directory = join_path(abspath(directory), "custom")
    make_sure_directories_exist([directory, custom_directory])

    return custom_directory


def limit_discovery_domains(directory, domains):

    flattened_domains = ",".join(
        list(
            filter(lambda x: x != "any", set((i for s in domains for i in s)))
        )
    )

    if flattened_domains:
        DISCOVERY_CONFIG["DISCOVERY_DOMAINS"] = flattened_domains
        print("Limiting domains to {}".format(flattened_domains))
        

def setup_discovery(directory, custom_directory, domains):
    limit_discovery_domains(directory, domains)
    volume = launch_discovery(custom_directory=custom_directory)
    wait_for_discovery_launch()
    return volume


def submit_transcript(
    transcript, intent_whitelist=["any"], domain_whitelist=["any"]
):
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
    response = requests.post(DISCOVERY_URL, json=payload)
    if not response.status_code == 200:
        LOGGER.error(
            "Request was not successful. Response Status Code: {}".format(
                response.status_code
            )
        )
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


def shutdown_discovery(shutdown=True):
    """
    Shuts down the Discovery engine Docker container
    """
    if not shutdown:
        return

    LOGGER.info("Shutting down Discovery")
    try:
        subprocess.call("docker rm -f {}".format(CONTAINER_NAME), shell=True)
    except Exception as exc:
        LOGGER.exception(exc)
    time.sleep(3)
