import os

DISCOVERY_CONFIG = {
  "GKT_USERNAME": os.environ.get("GKT_USERNAME", "username"),
  "GKT_SECRETKEY": os.environ.get("GKT_SECRETKEY", "password"),
  "GKT_API": "https://scribeapi.greenkeytech.com/",
  "NUMBER_OF_INTENTS": "2",
  "MAX_NUMBER_OF_ENTITIES": "3",
  "STRUCTURE_CONFIDENCE_THRESHOLD": "0.8",
  "SORT_ENTITIES_BY_LENGTH": "True",
  "PORT": "1234",  # Port that Discovery will bind to on the Docker daemon, change if port is taken already
}

CONTAINER_NAME = "discovery-dev"
DISCOVERY_PORT = "1234"  # This is the port you will POST to, e.g. curl localhost:1234
DISCOVERY_SHUTDOWN_SECRET = "greenkeytech"
DISCOVERY_HOST = "localhost"
DISCOVERY_IMAGE_NAME = "docker.greenkeytech.com/discovery"

TIMEOUT = 10
RETRIES = 5
