#!/usr/bin/env python3
import sys

# import pytest to ensure that pytest parametrizes this test with any provided interpreter directory
import pytest

from validate_yaml import validate_all_files


def test_directory(interpreter_directory):
    """
    Test a directory
    """
    validate_all_files(interpreter_directory)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
