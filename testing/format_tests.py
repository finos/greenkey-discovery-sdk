#!/usr/bin/env python3


def remove_all_whitespace_from_string(input_string):
    while "  " in input_string:
        input_string = input_string.replace("  ", " ")
    return input_string.strip()


def clean_list(input_list):
    return [strip_extra_whitespace(v) for v in input_list]


def clean_dict(input_dict):
    output_dict = {}
    for k, v in input_dict.items():
        output_dict[strip_extra_whitespace(k)] = strip_extra_whitespace(v)
    return output_dict


def strip_extra_whitespace(payload):
    """
    Cut leading and trailing whitespace as well as double spaces everywhere
    Accepts lists, strings, and dictionaries
    >>> strip_extra_whitespace("this is  a cat")
    'this is a cat'
    >>> strip_extra_whitespace(" this is a cat")
    'this is a cat'
    >>> strip_extra_whitespace({"transcript": "euro five week         "})
    {'transcript': 'euro five week'}
    """
    if isinstance(payload, str):
        payload = remove_all_whitespace_from_string(payload)
    elif isinstance(payload, list):
        payload = clean_list(payload)
    elif isinstance(payload, dict):
        payload = clean_dict(payload)
    return payload
