import json
import os
import subprocess

os.environ['USE_DOCKER_VOLUME'] = "False"
os.environ['TRAIN_MODELS'] = "False"

from testing.discovery_interface import (
    log_discovery,
    reload_discovery_config,
    setup_discovery,
    submit_transcript,
    shutdown_discovery,
    validate_custom_directory,
)

from testing.discovery_config import CONTAINER_NAME

from interactive_sdk import (
    format_entities,
    get_entities_from_discovery,
)

INTERPRETER_DIRECTORY = os.environ.get('INTERPRETER_DIRECTORY', 'examples/calling_room')
DISCOVERY_DOMAINS = [
    subprocess.check_output("""
    find {} -follow -name "*.yaml" | while read line; do grep "domain:" $line; done \
    | awk '{{print $NF}}' | sed -e 's/^\"//' -e 's/\"$//' | uniq | tr '\n' ','
    """.format(INTERPRETER_DIRECTORY),
                            shell=True).decode('utf-8').strip(",").split(",")
]


def start():
    setup_discovery(
        INTERPRETER_DIRECTORY,
        validate_custom_directory(INTERPRETER_DIRECTORY),
        DISCOVERY_DOMAINS,
    )


def stop():
    shutdown_discovery()


def reload():
    reload_discovery_config()


def restart():
    stop()
    start()


def log():
    log_discovery()


def return_json_data(data, raw=False):
    if raw:
        return data
    print(json.dumps(data, sort_keys=True, indent=2))


def get_schema(intent, schema_key, transcript, raw_data=False):
    payload = submit_transcript(transcript, intent_whitelist=[intent])
    if schema_key in payload:
        return return_json_data(payload[schema_key], raw_data)
    else:
        return "Schema key {} not found".format(schema_key)


def get_response(intent, transcript, raw_data=False):
    payload = submit_transcript(transcript, intent_whitelist=[intent])
    return return_json_data(payload, raw_data)


def get_entities(intent, transcript):
    payload = submit_transcript(transcript, intent_whitelist=[intent])
    entities = get_entities_from_discovery(payload)
    config = {"entities": [entity["label"] for entity in entities]}
    print(format_entities(entities, config))


def get_token_logs(intent, transcript):
    submit_transcript(transcript, intent_whitelist=[intent])
    logs = subprocess.check_output("docker logs {}".format(CONTAINER_NAME),
                                   stderr=subprocess.STDOUT,
                                   shell=True).decode('utf-8').split("\n")
    output = []
    separators = 0
    for line in reversed(logs):
        separators += line.startswith("===")
        if separators > 0:
            output.append(line)
        if separators == 2:
            break
    return reversed(output)


def get_tokens(intent, transcript):
    print("\n".join(get_token_logs(intent, transcript)))


def get_token_coverage(intent, transcript):
    token_lines = list(get_token_logs(intent, transcript))[3:-1]
    tokens = [[w for w in t.split(" ") if w][-2:] for t in token_lines]
    transcript = [w[-1] for w in tokens]
    coverage = [("*" if w[0] != "None" else " ") * len(w[-1]) for w in tokens]
    print("""
    Recognized parts of the transcript are denoted with '*'
    
    {0}
    {1}
    """.format(' '.join(transcript), ' '.join(coverage)))
