#!/usr/bin/env python
"""This module will launch Discovery on http://localhost:1234

This file will automatically scan for a folder of discovery binaries.
If the binaries are not detected, the script will launch the Discovery docker container.

Available functions:
- launch_discovery: Starts discovery container or binaries
"""
import fnmatch
from multiprocessing import Process
import os
import subprocess
import sys

from discovery_config import DISCOVERY_CONFIG, DISCOVERY_PORT, DISCOVERY_IMAGE_NAME
from discovery_config import CONTAINER_NAME


def launch_discovery(custom_directory=None,
                     type=None,
                     port=None,
                     discovery_config=None,
                     container_name=None):
    """Launches the Discovery engine either via docker container or via compiled binaries.

    Args:
        custom_directory: File path to the custom directory would like uploaded to discovery.
        type: String, can either be 'docker' or 'binaries'
    """
    if custom_directory is None:
        custom_directory = os.getcwd()
    if port is None:
        port = DISCOVERY_PORT
    if discovery_config is None:
        discovery_config = DISCOVERY_CONFIG
    if container_name is None:
        container_name = CONTAINER_NAME

    if type is None:
        type = _determine_discovery_launch_type()

    if type == 'docker':
        return _launch_container(custom_directory, port, discovery_config,
                                 container_name)

    return _launch_binaries(custom_directory, port, discovery_config)


def _determine_discovery_launch_type():
    binaries_directory = _detect_binaries_file()
    if binaries_directory:
        return 'binaries'
    return 'docker'


def _launch_container(custom_directory, port, discovery_config, container_name):
    """
    launches the Discovery docker container.

    :param custom_directory: `custom/` directory with config adn data files for custom interpreter:
    intents.json, schema.json (optional), entities/ (optional) #TODO changes in development
    any supporting `.txt` files requisite for training or testing intents and/or entities

    All other variables are imported from `discovery_config.py`
     - required: valid GKT_USERNAME & GKT_SECRET_KEY
     - required if values used by running container: DISCOVERY_PORT, PORT, CONTAINER_NAME,
     - additional values modify Discovery behavior!

    :param port: DISCOVERY_PORT -> port outside container: location to send POST requests
    :param discovery_config: DISCOVERY_CONFIG: dict; see for specifics
    :param container_name: CONTAINER_NAME; value of `docker run` param `--name`
        default: `discovery-dev`
        recommend: select unique name when launching container (modify config script)

        IMPORTANT:
        CONTAINER_NAME: sets name of output log file in `launch_discovery.py`
        - also parameter required to launch container
    :return: launches Discovery container; default:
        mounts custom directory in examples/directions (modify under `__main__`
    """
    dico_dir = ["-v", "{}/dico:/dico".format(custom_directory)
                ] if os.path.isdir(custom_directory + '/dico') else []

    try:
        config_items = discovery_config.iteritems()
    except AttributeError:
        config_items = iter(discovery_config.items())

    # yapf: disable
    launch_command = ' '.join(
        ["docker", "run", "--rm", "-d"] +
        ["--name", container_name] +
        ["-v", '"{}":/custom'.format(custom_directory)] +
        ["-p", "{}:{}".format(port, discovery_config["PORT"])] +
        dico_dir +
        ["-e {}={}".format(k, v) for k, v in config_items] +
        [DISCOVERY_IMAGE_NAME]
    )
    # yapf: enable
    print("Launching Discovery from Container: {}\n".format(launch_command))

    subprocess.call(launch_command, shell=True)


def _launch_binaries(custom_directory):
    """launches Discovery from the compiled binaries."""
    binaries_directory = _detect_binaries_file()
    if binaries_directory:
        sys.path.append(os.path.abspath(binaries_directory))
        from run import find_definition_files_and_copy_them_to_appropriate_location
        find_definition_files_and_copy_them_to_appropriate_location(
            os.path.join(custom_directory), os.path.abspath(binaries_directory))

        sys.path.append(os.path.join(binaries_directory, 'discovery'))

        print("Launching Discovery from Binaries: {}\n".format(binaries_directory))

        os.environ["SERVICE_NAME"] = "discovery"
        from discovery.server import main

        proc = Process(target=main, args=())
        proc.start()


def _detect_binaries_file():
    """Returns the absolute path of the binaries directory."""
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, 'discovery_binaries_*') and not file.endswith(
                '.tar.gz') and not file.endswith('.zip'):
            return os.path.abspath(file)
    return None


if __name__ == '__main__':
    try:
        project_name = sys.argv[1]
    except IndexError:
        project_name = 'directions'  # defaults to examples/directions

    project_custom_directory = os.path.join(os.getcwd(), 'examples', project_name,
                                            'custom')
    launch_discovery(custom_directory=project_custom_directory)
