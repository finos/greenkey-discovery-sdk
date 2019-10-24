import os

try:
    from secrets import GKT_USERNAME, GKT_SECRETKEY
except ImportError:
    GKT_USERNAME = "username"
    GKT_SECRETKEY = "password"

DISCOVERY_CONFIG = {
    "GKT_USERNAME": os.environ.get("GKT_USERNAME", GKT_USERNAME),
    "GKT_SECRETKEY": os.environ.get("GKT_SECRETKEY", GKT_SECRETKEY),
    "GKT_API": "https://scribeapi.greenkeytech.com/",
    "NUMBER_OF_INTENTS": "1",
    "MAX_NUMBER_OF_ENTITIES": "100",
    "GROUP_ENTITIES": "False", # to be deprecated
    "SORT_ENTITIES_BY_LENGTH": "True",  # Default is False
    "HIDE_EMPTY_ENTITIES": "True",
    "ENTITY_PROBABILITY_THRESHOLD": "0.01",
    "STRUCTURE_CONFIDENCE_THRESHOLD": "0.8",  # Default is 0.01
    "WORD_PROBABILITY_THRESHOLD": "5e-3",
    "MAX_WORDS_PER_TIMESLOT": "50",
    "USE_CUSTOM_JSON_SCHEMA": "True",
    "SUPPRESS_DEFAULT_OUTPUT": "False",
    "FILE_LOG_LEVEL": "verbose",  # options for increasing log verbosity: payload, debug, verbose
    "SCHEMA_ENTITY_REPLACEMENT_POLICY": "Best",
    "USE_SAVED_MODELS": "False",     # if True, pretrained model should be in /scribediscovery/models
    "STRIP_TEXT_FORMAT": "False",
    "EXPLICIT_REGEX": "True",
    "FORMAT_ENTITY": "True",
    "VALIDATE_ENTITY": "True",
    "PORT": "1234",  # Port that Discovery will bind to on the Docker daemon, change if port is taken already}
}

CONTAINER_NAME = "discovery-dev"
DISCOVERY_PORT = "1234"  # This is the port you will POST to, e.g. curl localhost:1234
DISCOVERY_SHUTDOWN_SECRET = "greenkeytech"
DISCOVERY_HOST = "localhost"
TAG = os.environ.get("TAG", "master")
DISCOVERY_IMAGE_NAME = "docker.greenkeytech.com/discovery:{}".format(TAG)

TIMEOUT = 20
RETRIES = 15
