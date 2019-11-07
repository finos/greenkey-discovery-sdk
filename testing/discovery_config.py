import os

# This is the port you will POST to, e.g. curl localhost:1234
DISCOVERY_PORT = "1234"
DISCOVERY_HOST = "localhost"
TAG = os.environ.get("TAG", "latest")

TIMEOUT = 20
RETRIES = 15

DISABLE_INTENTS_WHITELIST = False

CONTAINER_NAME = "discovery-dev"
DISCOVERY_SHUTDOWN_SECRET = "greenkeytech"
DISCOVERY_IMAGE_NAME = "docker.greenkeytech.com/discovery:{}".format(TAG)

DISCOVERY_CONFIG = {
    "LICENSE_KEY": os.environ.get('LICENSE_KEY', ''),
    "NUMBER_OF_INTENTS": "1",
    "MAX_NUMBER_OF_ENTITIES": "100",
    
    # options for increasing log verbosity: payload, debug, verbose
    "CONSOLE_LOG_LEVEL": "verbose",
    
    # if True, pretrained model should be in /scribe/discovery/models
    "USE_SAVED_MODELS": "False",
    
    # Port that Discovery will bind to on the Docker daemon, change if port is taken already
    "PORT": DISCOVERY_PORT,
}
