#!/usr/bin/python
'''
Utility functions for discovery
'''
from __future__ import print_function

# global imports
import os


def json_utf_8_encoding(input):
  '''returns json file with utf-8 encoded strings, not unicode. Important for regex stuff '''
  if isinstance(input, dict):
    return {json_utf_8_encoding(key): json_utf_8_encoding(value) for key, value in input.iteritems()}
  elif isinstance(input, list):
    return [json_utf_8_encoding(element) for element in input]
  elif isinstance(input, unicode):
    return input.encode('utf-8')
  else:
    return input


def _unique_pattern_tokens(entity_definition):
  return set([token for pattern in entity_definition['patterns'] for token_slot in pattern for token in token_slot])


def _unique_extra_tokens(entity_definition):
  if 'extraTokens' not in entity_definition:
    return set()
  return set([token['label'] for token in entity_definition['extraTokens']])


def validate_entity_definition(entity_definition):
  from inspect import isfunction
  if not isinstance(entity_definition, dict):
    raise Exception()
  if 'patterns' not in entity_definition:
    raise Exception('Your ENTITY_DEFINITION must contain a "patterns" key!')

  pattern_error_message = 'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists of strings.' \
                  'e.g. [[["NUM"], ["LETTER"]]]'
  if not isinstance(entity_definition['patterns'], list):
    raise Exception(pattern_error_message)
  for pattern in entity_definition['patterns']:
    if not isinstance(pattern, list):
      raise Exception(pattern_error_message)
    for token_slot in pattern:
      if not isinstance(token_slot, list):
        raise Exception(pattern_error_message)
      for token in token_slot:
        if not isinstance(token, str):
          raise Exception(pattern_error_message)

  pattern_tokens = _unique_pattern_tokens(entity_definition)
  extra_tokens = _unique_extra_tokens(entity_definition)
  for token in extra_tokens:
    if token not in pattern_tokens:
      raise Exception('The token {} is defined in "extraTokens" but is not used in any "patterns"'.format(token))
  built_in_tokens = ("NUM", "LETTER", "NUM_ORD", "NUM_PLURAL", "TIME_MONTH", "TIME_DAY", "TIME_WEEK")
  for token in pattern_tokens:
    if token not in extra_tokens and token not in built_in_tokens:
      raise Exception('The token \"{0}\" is used in "patterns" but is not a built in token, please define \"{0}\" in "extraTokens"'.format(token))

  if 'extraTokens' in entity_definition:
    if not isinstance(entity_definition['extraTokens'], tuple):
      raise Exception('The "extraTokens" property must be a tuple!')
  if 'spacing' in entity_definition:
    if not isinstance(entity_definition['spacing'], dict):
      raise Exception('The "spacing" property must be a dictionary!')
  if 'extraCleaning' in entity_definition:
    if not isinstance(entity_definition['extraCleaning'], dict):
      raise Exception('The "extraCleaning" property must be a dictionary!')
    for token in entity_definition['extraCleaning']:
      if not isfunction(entity_definition['extraCleaning'][token]):
        raise Exception('Each property in "extraCleaning" must be a valid function!')
  if 'ontological_tags' in entity_definition:
    if not isinstance(entity_definition['ontological_tags'], bool):
      raise Exception('The "ontological_tags" property must be a boolean!')
  if 'entityCleaning' in entity_definition:
    if not isfunction(entity_definition['entityCleaning']):
      raise Exception('The "entityCleaning" property must be a function!')
  if 'entityValidation' in entity_definition:
    if not isfunction(entity_definition['entityValidation']):
      raise Exception('The "entityValidation" property must be a function!')

  collapsible_pattern_message = 'The "collapsiblePatterns" property must be a tuple of tuples!'
  if 'collapsiblePatterns' in entity_definition:
    if not isinstance(entity_definition['collapsiblePatterns'], tuple):
      raise Exception(collapsible_pattern_message)
    for collapsible_pattern in entity_definition['collapsiblePatterns']:
      if not isinstance(collapsible_pattern, tuple):
        raise Exception(collapsible_pattern_message)


def set_boolean(variable, enabled=True, default=False):
  if enabled and variable in os.environ:
    return (os.environ[variable] == "True")
  return default


def set_integer(variable, default):
  if variable in os.environ:
    try:
      return int(os.environ[variable])
    except Exception:
      pass
  return default


def set_float(variable, default):
  if variable in os.environ:
    try:
      return float(os.environ[variable])
    except Exception:
      pass
  return default
