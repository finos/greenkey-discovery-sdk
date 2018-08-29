#!/usr/bin/python
'''
Utility functions for discovery
'''
from __future__ import print_function, absolute_import


def json_utf_8_encoding(input):
    '''returns json file with utf-8 encoded strings, not unicode. Important for regex stuff '''
    if isinstance(input, dict):
        return {json_utf_8_encoding(key): json_utf_8_encoding(value) for key, value in input.iteritems()}

    if isinstance(input, list):
        return [json_utf_8_encoding(element) for element in input]

    if isinstance(input, unicode):
        return input.encode('utf-8')

    return input
