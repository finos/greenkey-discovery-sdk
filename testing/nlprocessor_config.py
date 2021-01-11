#!/usr/bin/env python3

import os

from testing.shared_config import CONFIG

# This is the port you will POST to, e.g. curl 127.0.0.1:1235
NLPROCESSOR_PORT = "1235"
NLPROCESSOR_HOST = "127.0.0.1"
TAG = os.environ.get("TAG", "latest")

NLPROCESSOR_TIMEOUT = int(os.environ.get("NLPROCESSOR_TIMEOUT", "5"))
NLPROCESSOR_RETRIES = int(os.environ.get("NLPROCESSOR_RETRIES", "60"))

DISABLE_INTENTS_WHITELIST = False

NLPROCESSOR_CONTAINER_NAME = "nlprocessor-dev"
NLPROCESSOR_IMAGE_NAME = "docker.greenkeytech.com/NLPROCESSOR:{}".format(TAG)

NLPROCESSOR_CONFIG = {
    # options for increasing log verbosity: debug, info, warning, error, critical
    "LOG_LEVEL": "debug",
    # Port that NLPROCESSOR will bind to on the Docker daemon, change if port is taken already
    "PORT": NLPROCESSOR_PORT,
}

NLPROCESSOR_CONFIG.update(CONFIG)
