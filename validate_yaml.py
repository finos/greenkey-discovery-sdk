#!/usr/bin/env python3
"""
Validates all yaml files by testing if entities and intents
are unique and if all files mentioned are present
"""

import glob
import os
import sys

import yaml
from fire import Fire

from validate_regex import validate_regex_in_yaml_file


def print_or_throw_error(condition, success_message, failure_message, code=1):
    "Print a message on success/failure of condition"
    if condition:
        print(success_message)
    else:
        assert False, failure_message


def validate_elements(new_elements, known_elements):
    """
    Check new elements (entities or intents) against already identified elements.
    Returns elment list, success_code where
    element list is the bad entities if it failed
    >>> validate_elements([1,2,3], [])
    ([1, 2, 3], True)
    >>> validate_elements([1,2,2], [])
    ([2], False)
    >>> validate_elements([], [])
    ([], True)
    >>> validate_elements([1,2,2], [2])
    ([2], False)
    >>> validate_elements([1,2], [2])
    ([2], False)
    """
    unique_elements = set(new_elements)
    is_unique = sorted(unique_elements) == sorted(new_elements)

    overlap = unique_elements.intersection(known_elements)
    is_known = bool(overlap)

    if not is_unique:
        duplicated_elements = set(elem for elem in new_elements
                                  if new_elements.count(elem) > 1)
        overlap = overlap.union(duplicated_elements)
    failure = is_known or not is_unique
    return (list(overlap if failure else unique_elements), not failure)


def validate_file_exists(file_name):
    "This wrapper checks if a file exists."
    if not os.path.isfile(file_name):
        throw_error("{} does not exist".format(file_name))
    return True


def key_is_present(data, key):
    "Check if key is present within the data object."
    return key in data


def validate_files(structured_dict):
    "For an intent or entity, validate existence of all files."
    files_to_check = [
        obj.get("files", []) +
        ([validate_file_exists(obj["file"])] if obj.get("file") else [])
        for obj in structured_dict.values()
    ]
    for target_file in files_to_check:
        validate_file_exists(target_file)


def no_duplicate_values(data, key):
    """
    Check if a dict (list) has duplicate keys (elements).
    If the input is a list of dictionaries, this will check
    the "label" attribute by default
    >>> no_duplicate_values({"intents": ["a", "a"]}, "intents")
    False
    >>> no_duplicate_values({"intents": ["a"]}, "intents")
    True
    >>> no_duplicate_values({"entities": {"a": []}}, "entities")
    True
    >>> no_duplicate_values({"entities": {"a": []}, "b": []}, "entities")
    True
    """
    obj = data.get(key, [])
    return sorted(obj) == sorted(set(obj))


def check_key(yaml_file, data_dict, key, known_values):
    """
    Performs check on entities for yaml file
    >>> check_key("test.yaml", {"intents": ["a"]}, "intents", [])
    File test.yaml does not duplicate any intents
    No intents in test.yaml duplicate previous ones
    ['a']

    >>> check_key("test.yaml", {"entities": ["a"]}, "entities", [])
    File test.yaml does not duplicate any entities
    No entities in test.yaml duplicate previous ones
    ['a']

    """
    new_values = set()
    print_or_throw_error(
        no_duplicate_values(data_dict, key),
        "File {} does not duplicate any {}".format(yaml_file, key),
        "{} contains duplicate {}".format(yaml_file, key),
    )
    new_values, success_code = validate_elements(data_dict.get(key, []), known_values)

    print_or_throw_error(
        success_code,
        "No {} in {} duplicate previous ones".format(key, yaml_file),
        "{} contains {} duplicated elsewhere, namely {}".format(
            yaml_file, key, str(new_values)),
    )
    return new_values


def validate_yaml_file(yaml_file, known_entities, known_intents):
    "Perform per-file validation on an individual yaml file."
    with open(yaml_file) as config:

        # read it
        data = yaml.load(config, Loader=yaml.FullLoader)

        # make sure either entities or intents exists as a top level key
        if len(set(["entities", "intents"]).intersection(data.keys())) == 0:
            throw_error("No top level keys for intents or entities found in {}".format(
                yaml_file))

        new_entities = check_key(yaml_file, data, "entities", known_entities)

        new_intents = check_key(yaml_file, data, "intents", known_intents)

        # to do list:
        # check ast eval of all functions (inline lambdas and of python files)

        return new_entities, new_intents


def validate_all_files(interpreter_directory):
    "Loop over yaml files and validate."
    if not interpreter_directory:
        return
    known_entities = set()
    known_intents = set()
    for yaml_file in glob.glob(os.path.join(interpreter_directory, "*.yaml"),
                               recursive=True):
        validate_regex_in_yaml_file(yaml_file)
        new_entities, new_intents = validate_yaml_file(yaml_file, known_entities,
                                                       known_intents)
        known_entities.update(new_entities)
        known_intents.update(new_intents)


if __name__ == "__main__":
    Fire(validate_all_files)
