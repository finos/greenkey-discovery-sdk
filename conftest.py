#!/usr/bin/env python3
"""
Set arguments for pytest invocations and load fixtures into test_discovery.py
"""
import glob
import logging
from os.path import dirname
from os.path import join as join_path

import pytest
import yaml

from launch import launch_docker_compose, teardown_docker_compose
from testing.discovery_interface import (
    make_sure_directories_exist,
    validate_interpreter_directory,
)
from testing.parse_tests import (
    add_extension_if_missing,
    expand_wildcard_tests,
    load_tests,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s - %(asctime)s - %(name)s :: %(message)s",
)

LOGGER = logging.getLogger(__name__)


def validate_yaml(intents_config_file):
    """
    Validate definitions.yaml
    """
    with open(intents_config_file) as yaml_file:
        yaml_file_contents = yaml_file.read()
        yaml.load(yaml_file_contents, Loader=yaml.FullLoader)


def pytest_addoption(parser):
    """
    Add interpreter-directory and tests options for pytest invocation
    """
    parser.addoption(
        "--interpreter-directory",
        action="store",
        default=None,
        help="Directory containing YAML files for your intents",
    )
    parser.addoption(
        "--tests",
        nargs="+",
        action="store",
        default=[],
        help="List of text files to test",
    )


def check_discovery_setup(interpreter_directory, tests):
    """
    check for interpreter directory
    """
    if interpreter_directory:
        validate_interpreter_directory(interpreter_directory)

        # check all files
        yaml_files = glob.glob(join_path(interpreter_directory, "*.yaml")) + glob.glob(
            join_path(interpreter_directory, "*.yml"))
        for yaml_file in yaml_files:
            validate_yaml(yaml_file)

        assert (tests
                is not None), "You must specify a list of text files containing tests"


def identify_what_to_launch(tests):
    """
    Given input tests, identify what the launch target is
    """
    _, intents, nlp_models, _ = load_test_files(tests)
    if all(map(any, (intents, nlp_models))):
        target = "everything"
    elif any(nlp_models):
        target = "nlprocessor"
    else:
        target = "discovery"

    return target


def clean_test_arguments(tests):
    """
    Convert test from input into dictionaries
    """
    test_files = [
        add_extension_if_missing(elem) for test in tests for elem in test.split(",")
    ]
    test_files = expand_wildcard_tests(test_files)

    make_sure_directories_exist(map(dirname, test_files))
    return test_files


def load_test_files(tests):
    """
    From a list of test files,
    return
    """
    test_files = clean_test_arguments(tests)
    test_dicts = []
    intents = []
    nlp_models = []
    test_names = []
    for test_file in test_files:
        (
            tests_from_this_file,
            test_intents,
            test_nlp_models,
        ) = load_tests(test_file)
        test_dicts += tests_from_this_file
        intents += [test_intents] * len(tests_from_this_file)
        nlp_models += [test_nlp_models] * len(tests_from_this_file)
        test_names += [
            f"{test_file}-{test_dict.get('test','')}"
            for test_dict in tests_from_this_file
        ]
    return test_dicts, intents, nlp_models, test_names


def pytest_generate_tests(metafunc):
    """
    Parametrize test function to iterate over provided tests
    """
    tests = metafunc.config.getoption("tests")

    test_dicts, intents, nlp_models, test_names = load_test_files(tests)

    # parametrize test_nlp which usess both nlprocessor and discovery
    if {"test_dict", "intents", "nlp_models",
            "test_name"}.issubset(metafunc.fixturenames):
        metafunc.parametrize(
            "test_dict,intents,nlp_models,test_name",
            zip(test_dicts, intents, nlp_models, test_names),
        )

    interpreter_directory = metafunc.config.getoption("interpreter_directory")

    # parametrize test_nlp which usess both nlprocessor and discovery
    if "interpreter_directory" in metafunc.fixturenames:
        metafunc.parametrize(
            "interpreter_directory",
            [interpreter_directory],
        )

    # parametrize test_nlp which usess both nlprocessor and discovery
    if "tests" in metafunc.fixturenames:
        metafunc.parametrize(
            "tests",
            [tests],
        )
