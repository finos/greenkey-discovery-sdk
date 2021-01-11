#!/usr/bin/env python3

import glob
import io
import logging
import os
import sys
import tarfile
from enum import Enum

import docker
import dotenv
import requests
from compose.cli.main import main as docker_compose
from fire import Fire
from mock import patch
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

env = dotenv.dotenv_values("client.env")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s - %(asctime)s - %(name)s :: %(message)s",
)

LOGGER = logging.getLogger(__name__)

BUILTIN_DISCOVERY_MODELS = "builtin-discovery-models"
CUSTOM_DISCOVERY_INTERPRETER = "custom-discovery-interpreter"
BUILTIN_NLPROCESSOR_MODELS = "builtin-nlprocessor-models"

class RetryRequest(Retry):
    """
    Custom retry class with max backoff set to TIMEOUT from client.env
    """

    BACKOFF_MAX = float(env["TIMEOUT"])


retries = RetryRequest(total=int(env["RETRIES"]),
                       backoff_factor=1.0,
                       status_forcelist=[500, 502, 503, 504])
request_session = requests.Session()
request_session.mount("http://", HTTPAdapter(max_retries=retries))


class LaunchTarget(Enum):
    everything = "everything"
    discovery = "discovery"
    nlprocessor = "nlprocessor"


def pull_image(image):
    client = docker.client.from_env()
    try:
        client.images.pull(image)
    except:
        LOGGER.warning(
            "Unable to pull latest %s. Using image as found in local registry", image)
        pass


def load_builtin_discovery_models():
    """
    Create a docker volume,
    attach it to a busybox container,
    and load the GK interpreter models into that container
    """

    client = docker.client.from_env()

    # copy default models in
    builtin_models = client.volumes.create(name=BUILTIN_DISCOVERY_MODELS)
    initdiscovery_tag = env["INIT_DISCOVERY_TAG"]
    initdiscovery_project = "docker.greenkeytech.com/greenkey-discovery-sdk-private"
    initdiscovery_image = f"{initdiscovery_project}:{initdiscovery_tag}"
    pull_image(initdiscovery_image)
    _ = client.containers.run(
        initdiscovery_image,
        auto_remove=True,
        volumes={builtin_models.name: {
            "bind": "/models",
            "mode": "rw"
        }},
    )


def load_builtin_nlprocessor_models():
    """
    Create a docker volume,
    attach it to a busybox container,
    and load the GK nlprocessor models into that container
    """

    client = docker.client.from_env()

    # copy default models in
    builtin_models = client.volumes.create(name=BUILTIN_NLPROCESSOR_MODELS)
    initnlprocessor_tag = env["INIT_NLPROCESSOR_TAG"]
    initnlprocessor_project = "docker.greenkeytech.com/nlpmodelcontroller"
    initnlprocessor_image = f"{initnlprocessor_project}:{initnlprocessor_tag}"
    pull_image(initnlprocessor_image)
    _ = client.containers.run(
        initnlprocessor_image,
        auto_remove=True,
        volumes={builtin_models.name: {
            "bind": "/models/transformers",
            "mode": "rw"
        }},
    )


def load_custom_model(interpreter_directory):
    """
    Create a docker volume, attach it to a busybox container, and load our interpreter into that container
    """
    if not os.path.isdir(interpreter_directory):
        raise Exception(f"Interpreter directory {interpreter_directory} not found")

    # copy custom model in
    client = docker.client.from_env()
    vol = client.volumes.create(name=CUSTOM_DISCOVERY_INTERPRETER)
    source = interpreter_directory
    destination = "/data"
    busybox_image = f"busybox:{env['BUSYBOX_TAG']}"
    pull_image(busybox_image)
    busybox = client.containers.run(
        busybox_image,
        "sleep infinity",
        auto_remove=True,
        detach=True,
        volumes={vol.name: {
            "bind": destination,
            "mode": "rw"
        }},
    )
    file_like_object = io.BytesIO()
    with tarfile.open(fileobj=file_like_object, mode="w") as tar:
        for fl in glob.glob(os.path.join(source, "*")):
            tar.add(fl, arcname=fl.replace(source, ""))
    file_like_object.seek(0)
    data = file_like_object.read()
    busybox.put_archive(destination, data)
    busybox.remove(force=True)


def create_dummy_custom_model():
    """
    Create a docker volume that contains nothing so docker-compose still works
    """
    # copy custom model in
    client = docker.client.from_env()
    client.volumes.create(name=CUSTOM_DISCOVERY_INTERPRETER)


def wait_on_service(address):
    return request_session.get("/".join([address, "ping"]),
                               timeout=float(env["TIMEOUT"]))


def wait_for_everything(target):
    """
    Wait for all services as necessary
    """
    if target in [LaunchTarget.discovery, LaunchTarget.everything]:
        wait_on_service(":".join([env["DISCOVERY_HOST"], env["DISCOVERY_PORT"]]))
    if target in [LaunchTarget.nlprocessor, LaunchTarget.everything]:
        wait_on_service(":".join([env["NLPROCESSOR_HOST"], env["NLPROCESSOR_PORT"]]))


def check_for_license():
    """
    Codify license check
    """
    assert (env["LICENSE_KEY"] !=
            ""), "LICENSE_KEY needed. Please set in your environment or client.env"


def create_volumes(target, interpreter_directory):
    """
    Create volumes as needed
    """

    if interpreter_directory:
        load_custom_model(interpreter_directory)
    else:
        create_dummy_custom_model()

    if target in [LaunchTarget.discovery, LaunchTarget.everything]:
        load_builtin_discovery_models()
    if target in [LaunchTarget.nlprocessor, LaunchTarget.everything]:
        load_builtin_nlprocessor_models()


def stand_up_compose(target):
    """
    Stand up compose based on target
    """
    args = ["docker-compose", "--env-file", "client.env"]

    if target in [LaunchTarget.discovery, LaunchTarget.everything]:
        discovery_image = f"docker.greenkeytech.com/discovery:{env['DISCOVERY_TAG']}"
        pull_image(discovery_image)
        args += ["-f", "discovery.yaml"]
    if target in [LaunchTarget.nlprocessor, LaunchTarget.everything]:
        nlprocessor_image = (
            f"docker.greenkeytech.com/nlprocessor:{env['NLPROCESSOR_TAG']}")
        pull_image(nlprocessor_image)
        args += ["-f", "nlprocessor.yaml"]

    args += ["up", "-d", "--force-recreate"]
    with patch.object(sys, "argv", args):
        docker_compose()


def launch_docker_compose(target="everything", interpreter_directory=None):
    """
    Launch docker compose with either both discovery and nlprocessor or just one
    """
    check_for_license()

    target = LaunchTarget(target)

    create_volumes(target, interpreter_directory)

    stand_up_compose(target)

    # block until ready
    wait_for_everything(target)


def remove_volume(volume_name):
    client = docker.client.from_env()
    try:
        vol = client.volumes.get(volume_name)
        vol.remove()
    except docker.errors.NotFound:
        pass


def teardown_docker_compose():
    """
    Teardown docker compose
    """
    args = [
        "docker-compose",
        "--env-file",
        "client.env",
        "-f",
        "discovery.yaml",
        "-f",
        "nlprocessor.yaml",
        "down",
    ]
    with patch.object(sys, "argv", args):
        docker_compose()

    for volume_name in [
            "custom-discovery-interpreter",
            BUILTIN_DISCOVERY_MODELS,
            BUILTIN_NLPROCESSOR_MODELS,
    ]:
        remove_volume(volume_name)


if __name__ == "__main__":
    Fire(launch_docker_compose)
