#!/usr/bin/env python3

from validate_yaml import validate_all_files


def test_directory(interpreter_directory):
    """
    Test a directory
    """
    validate_all_files(interpreter_directory)
