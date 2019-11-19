#!/usr/bin/env python
"""This module will launch Discovery on http://localhost:1234

This file will automatically scan for a folder of discovery binaries.
If the binaries are not detected, the script will launch the Discovery docker container.

Available functions:
- launch_discovery: Starts discovery container or binaries
"""
import fnmatch
import os
import subprocess
import sys
import uuid
from multiprocessing import Process
from os.path import abspath, exists, isdir as is_dir, join as join_path

from testing.discovery_config import (
    CONTAINER_NAME, DISCOVERY_CONFIG, DISCOVERY_PORT, DISCOVERY_IMAGE_NAME
)


def launch_discovery(
    custom_directory=None,
    port=DISCOVERY_PORT,
    discovery_config=DISCOVERY_CONFIG,
    container_name=CONTAINER_NAME,
):
    """Launches the Discovery engine either via docker container or via compiled binaries.

    :param custom_directory: str; path to the 'custom/` directory to mount at Discovery launch
    :param type: str, options: 'docker' or 'binaries'
    """
    if not custom_directory:
        print(
            "Directory `custom/` not set. We are using the current working directory by default."
        )
        custom_directory = os.getcwd()
    if _determine_discovery_launch_type() == "docker":
        return _launch_container(
            custom_directory, port, discovery_config, container_name
        )
    return _launch_binaries(custom_directory)


def _determine_discovery_launch_type():
    binaries_directory = _detect_binaries_file()
    if binaries_directory:
        return "binaries"
    return "docker"


def load_data_into_docker_volume(custom_directory):
    """
    Copies a custom directory into a docker volume and returns that volume's name
    """

    volume = uuid.uuid1().hex
    subprocess.run(
        """docker volume create {0:}
                      docker run -v {0:}:/custom --name helper busybox true
                      docker cp {1:}/. helper:/custom
                      docker rm helper""".format(volume, custom_directory),
        shell=True,
    )
    return volume


def _launch_container(
    custom_directory, port, discovery_config, container_name
):
    """
    launches the Discovery docker container.

    :param custom_directory: `custom/` directory with yaml files defining interpreters
    and supporting `.txt` files requisite for training or testing intents and/or entities (if any)

    All other variables are imported from `discovery_config.py`
     - required: valid GKT_USERNAME & GKT_SECRET_KEY
     - required if Discovery is launched as Docker container: DISCOVERY_PORT, PORT, CONTAINER_NAME,
     - all optional params set to default values

    :param port: DISCOVERY_PORT -> port outside container: location to send POST requests
    :param discovery_config: DISCOVERY_CONFIG: dict; see for specifics
    :param container_name: CONTAINER_NAME; value of `docker run` param `--name`
        default: `discovery-dev`
        recommend: select unique name when launching container (modify config script)

    :return: launches Discovery container
        mounts custom/ directory in DISCOVERY_DIRECTORY (parameters of launch_discovery.py)
    """
    dico_dir = "{}/dico:/dico".format(custom_directory)
    dico_dir = ["-v", dico_dir
                ] if exists(dico_dir) and is_dir(dico_dir) else []

    # option to mount models/ directory if USED_SAVED_MODELS is True
    # model_dir = "{}/models".format(custom_directory)
    # model_dir = ["-v", model_dir] if exists(model_dir) and is_dir(model_dir) else []

    # load data into docker volume (supports remote docker executor)
    if os.environ.get("IN_A_CONTAINER", "True") != "False":
        volume = load_data_into_docker_volume(custom_directory)
        print("Stored configuration in docker volume {}".format(volume))
    else:
        volume = custom_directory

    launch_command = " ".join(
        ["docker", "run", "--rm", "-d"] + ["--name", container_name] +
        ["-v", "{}:/custom".format(volume)] +
        ["-p", "{}:{}".format(port, discovery_config["PORT"])] + dico_dir
        # + model_dir
        + ["-e {}={}".format(k, v)
           for k, v in discovery_config.items()] + [DISCOVERY_IMAGE_NAME]
    )
    print("Launching Discovery from Container: {}\n".format(launch_command))

    subprocess.call(launch_command, shell=True)

    return volume


def _launch_binaries(custom_directory):
    """launches Discovery from the compiled binaries."""
    binaries_directory = _detect_binaries_file()
    if binaries_directory:
        sys.path.append(abspath(binaries_directory))
        from run import find_definition_files_and_copy_them_to_appropriate_location

        find_definition_files_and_copy_them_to_appropriate_location(
            join_path(custom_directory), abspath(binaries_directory)
        )
        sys.path.append(join_path(binaries_directory, "discovery"))
        print(
            "Launching Discovery from Binaries: {}\n".
            format(binaries_directory)
        )

        os.environ["SERVICE_NAME"] = "discovery"
        from discovery.server import main

        proc = Process(target=main, args=())
        proc.start()


def _detect_binaries_file():
    """Returns the absolute path of the binaries directory."""
    for file in os.listdir("."):
        if (
            fnmatch.fnmatch(file, "discovery_binaries_*")
            and not file.endswith(".tar.gz") and not file.endswith(".zip")
        ):
            return abspath(file)
    return None


if __name__ == "__main__":
    try:
        project_name = sys.argv[1]
    except IndexError:
        project_name = "directions"  # defaults to examples/directions

    if os.path.isdir(os.path.join(os.getcwd(), project_name)):
        project_custom_directory = os.path.join(os.getcwd(), project_name)
    elif os.path.isdir(
        os.path.join(os.getcwd(), "examples", project_name, "custom")
    ):
        project_custom_directory = os.path.join(
            os.getcwd(), "examples", project_name, "custom"
        )
    launch_discovery(custom_directory=project_custom_directory)
