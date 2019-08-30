#!/usr/bin/env python3

import os
import pytest
import sys
from pathlib import Path

from test_discovery import validate_yaml


def test_validate_yaml():
    """Check that the yaml validator runs. Also serves to check that all built in
    definitions.yaml are yaml. if validate_yaml fails, exits with error code 1"""
    directories_to_test = next(os.walk("examples"))[1]
    for directory_to_test in directories_to_test:
        for yaml_file in Path("examples/{}".format(directory_to_test)).rglob("*.yaml"):
            validate_yaml(str(yaml_file))


if __name__ == "__main__":
    pytest.main(sys.argv)
