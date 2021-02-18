#!/usr/bin/env python3

"""
Stores utilities around testing schema
"""

import json

from testing.output_tests import print_errors


def _find_in_list(obj, key):
    for list_item in obj:
        item = _find(list_item, key)
        if item is not None:
            return item


def _find_in_dict(obj, key):
    if key in obj:
        return obj[key]
    for _, v in obj.items():
        item = _find(v, key)
        if item is not None:
            return item


def _find(obj, key):
    if isinstance(obj, list):
        return _find_in_list(obj, key)
    if isinstance(obj, dict):
        return _find_in_dict(obj, key)


def is_invalid_schema(schema, test_value):
    """
    Checks schema against tests with dictionary nesting

    >>> is_invalid_schema({"valid_key": "some_value"}, {"valid_key": "some_value"})
    False

    >>> is_invalid_schema({"invalid_key": "some_value"}, {"valid_key": "some_value"})
    True

    >>> is_invalid_schema(
    ... {"nested": {"valid_key": "some_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    False

    >>> is_invalid_schema(
    ... {"nested": {"invalid_key": "some_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    True

    >>> is_invalid_schema(
    ... {"nested": {"valid_key": "some_invalid_value", "another_key": "some_value"}},
    ... {"nested": {"valid_key": "some_value"}}
    ... )
    True

    >>> is_invalid_schema(
    ... {"nested": {"double": {"valid_key": "some_value", "another_key": "some_value"}}},
    ... {"nested": {"double": {"valid_key": "some_value"}}}
    ... )
    False

    >>> is_invalid_schema(
    ... {"nested": {"double": {"valid_key": "some_value", "another_key": "some_value"}}},
    ... {"nested": {"double": {"valid_key": "some_value"}, "some_key": "no_value"}}
    ... )
    True
    """
    if isinstance(test_value, dict):
        return any(
            is_invalid_schema(schema[k], test_value[k]) if k in schema else True
            for k in test_value.keys()
        )
    return schema != test_value


def test_schema(resp, test_value, logger, test_name=""):
    """
    For each key-value pair given in the schema test,
    recursively search the JSON response for the key,
    then make sure the value is correct
    """

    # Returning number of errors, so check for values that do not equal test case
    errs = {}
    for res in map(
        lambda k: {k: _find(resp, k)}
        if is_invalid_schema(_find(resp, k), test_value[k])
        else {},
        list(test_value.keys()),
    ):
        errs.update(res)

    print_errors(test_name, test_value, errs, logger)

    return len(errs), json.dumps(errs)
