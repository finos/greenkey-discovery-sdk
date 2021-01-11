#!/usr/bin/env python3
"""
This script accepts a list of yaml files and throws exit code 1 if any of them are invalid
"""

import re
import sys
from functools import partial

import yaml
from fire import Fire

from util.regex_expander import expand_these, expand_this


def recursive_search_dict(input_dict, target_key):
    """
    Recursively search input dictionary for target_key and append to a running list.
    """
    found = []
    for key, value in input_dict.items():
        if key == target_key:
            found += value if isinstance(value, list) else [value]
        elif isinstance(value, dict):
            found += recursive_search_dict(value, target_key)
        elif isinstance(value, (list, tuple)):
            for element in [_ for _ in value if isinstance(_, dict)]:
                found += recursive_search_dict(element, target_key)
    return found


def validate_found_regex(intent):
    """
    Validate regex entities
    """
    found_regex = recursive_search_dict(intent, "regex")
    try:
        list(map(re.compile, found_regex))
    except Exception as exc:
        print("Regex compilation failed for {} with error {}".format(yaml_file, exc))
        sys.exit(1)


def validate_entity_patterns(intent):
    """
    Validate entity patterns for an intent
    """
    found_patterns = recursive_search_dict(intent, "entity_patterns")
    try:
        list(map(expand_these, found_patterns))
    except Exception as exc:
        print("Regex compilation for entity patterns failed for {} with error {}".format(
            yaml_file, exc))
        sys.exit(1)


def validate_compound_entity_definition(entity, definition):
    """
    Validates a single entity's definition
    """
    try:
        expand_this(definition)
    except Exception as exc:
        print("Entity {} contains invalid pattern {} failed validation with error {}".
              format(entity, definition, exc))
        sys.exit(1)


def validate_compound_entities(intent):
    """
    Validates all entity definitions (given by any string with '@' in it)
    """
    for entity, values in intent.get("entities", {}).items():
        validate_this_entity = partial(validate_compound_entity_definition, entity)
        list(
            map(
                validate_this_entity,
                [value for value in values if isinstance(value, str) and "@" in value],
            ))


def validate_regex_in_yaml_file(yaml_file):
    """
    :param yaml_file: string for relative file path

    Throws exit code 1 if any regex do not compile
    """
    with open(yaml_file, "r") as config:
        intent = yaml.load(config, Loader=yaml.FullLoader)

    validate_found_regex(intent)
    validate_entity_patterns(intent)
    validate_compound_entities(intent)


def validate_all_files(*yaml_files):
    for yaml_file in yaml_files:
        validate_regex_in_yaml_file(yaml_file)


if __name__ == "__main__":
    Fire(validate_all_files)
