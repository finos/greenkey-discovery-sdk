#!/usr/bin/python
'''
Utility functions for discovery
'''
from __future__ import print_function
from inspect import isfunction
from .built_in_tokens import BUILT_IN_TOKENS


def _entity_definition_is_dictionary(entity_definition):
    if not _type_is_correct(entity_definition, dict):
        # this should throw an exception because no other tests can pass if this is not a dictionary
        raise Exception('Your ENTITY_DEFINITION must be a dictionary!')


def _validate_patterns_and_extraTokens_properties(entity_definition):
    errors = []
    pattern_errors = _validate_patterns_property(entity_definition)
    if pattern_errors:
        errors += pattern_errors

    extraToken_errors = _validate_extraTokens(entity_definition)
    if extraToken_errors:
        errors += extraToken_errors

    if not errors:
        # only run this if the 'patterns' and 'extraTokens' are valid
        errors += _validate_extra_tokens_and_pattern_tokens_against_each_other(entity_definition)
    return errors


def _validate_patterns_property(entity_definition):
    if 'patterns' not in entity_definition:
        return ['Your ENTITY_DEFINITION must contain a "patterns" property!']
    return _patterns_property_has_correct_value(entity_definition)


def _patterns_property_has_correct_value(entity_definition):
    pattern_error_message = [
        'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists '
        'of strings. e.g. [[["NUM"], ["LETTER"]]]'
    ]

    patterns = entity_definition['patterns']

    try:
        _find_error_with_patterns_property(patterns)
    except SyntaxError:
        return pattern_error_message


def _find_error_with_patterns_property(patterns):
    if not _type_is_correct(patterns, list):
        raise SyntaxError()
    _validate_pattern_in_patterns(patterns)


def _validate_pattern_in_patterns(patterns):
    for pattern in patterns:
        _throw_error_if_not_list(pattern)
        _validate_token_slot_in_pattern(pattern)


def _validate_token_slot_in_pattern(pattern):
    for token_slot in pattern:
        _throw_error_if_not_list(token_slot)
        _validate_token_in_token_slot(token_slot)


def _throw_error_if_not_list(item_list):
    if not _type_is_correct(item_list, list):
        raise SyntaxError()


def _validate_token_in_token_slot(token_slot):
    for token in token_slot:
        if not _type_is_correct(token, str):
            raise SyntaxError()


def _validate_extraTokens(entity_definition):
    error_message = _validate_property_type_if_present(entity_definition, 'extraTokens', tuple)
    if error_message:
        return error_message

    return _check_unique_extra_tokens(entity_definition)


def _check_unique_extra_tokens(entity_definition):
    if 'extraTokens' in entity_definition:
        for token in entity_definition['extraTokens']:
            error_message = _validate_token_of_extraTokens(token)
            if error_message:
                return error_message


def _validate_token_of_extraTokens(token):
    if not _type_is_correct(token, dict):
        return ['Your "extraTokens" must be a tuple of dictionaries!']
    if 'label' not in token:
        return ['Your "extraTokens" dictionaries must contain a "label" property!']
    if 'values' not in token:
        return ['Your "extraTokens" dictionaries must contain a "values" property!']


def _validate_extra_tokens_and_pattern_tokens_against_each_other(entity_definition):
    pattern_tokens = _unique_pattern_tokens(entity_definition)
    extra_tokens = _unique_extra_tokens(entity_definition)

    errors = []
    errors += _check_if_extraTokens_are_missing_from_patterns(extra_tokens, pattern_tokens)
    errors += _check_if_pattern_tokens_are_missing_from_extraTokens_or_built_in_tokens(
        pattern_tokens, extra_tokens, BUILT_IN_TOKENS
    )
    return errors


def _check_if_extraTokens_are_missing_from_patterns(extra_tokens, pattern_tokens):
    errors = []
    for token in extra_tokens:
        if token not in pattern_tokens:
            errors.append('The token "{}" is defined in "extraTokens" but is not used in any "patterns"'.format(token))
    return errors


def _check_if_pattern_tokens_are_missing_from_extraTokens_or_built_in_tokens(
    pattern_tokens, extra_tokens, built_in_tokens
):
    errors = []
    for token in pattern_tokens:
        if token not in extra_tokens and token not in built_in_tokens:
            errors.append(
                'The token \"{0}\" is used in "patterns" but is not a built in token, '
                'please define \"{0}\" in "extraTokens"'.format(token)
            )
    return errors


def _validate_extraCleaning(entity_definition):
    error_message = _validate_property_type_if_present(entity_definition, 'extraCleaning', dict)
    if error_message:
        return error_message
    if 'extraCleaning' in entity_definition:
        for token in entity_definition['extraCleaning']:
            if not _type_is_correct(entity_definition['extraCleaning'][token], 'function'):
                return ['Each property in "extraCleaning" must be a function!']


def _validate_spacing(entity_definition):
    return _validate_property_type_if_present(entity_definition, 'spacing', dict)


def _validate_ontological_tags(entity_definition):
    return _validate_property_type_if_present(entity_definition, 'ontological_tags', bool)


def _validate_entityCleaning(entity_definition):
    return _validate_property_type_if_present(entity_definition, 'entityCleaning', 'function')


def _validate_entityValidation(entity_definition):
    return _validate_property_type_if_present(entity_definition, 'entityValidation', 'function')


def _validate_collapsiblePatterns(entity_definition):
    collapsible_pattern_message = 'The "collapsiblePatterns" property must be a tuple of tuples!'
    error_message = _validate_property_type_if_present(entity_definition, 'collapsiblePatterns', tuple)
    if error_message:
        return error_message
    if 'collapsiblePatterns' in entity_definition:
        for collapsible_pattern in entity_definition['collapsiblePatterns']:
            if not _type_is_correct(collapsible_pattern, tuple):
                return collapsible_pattern_message


def _validate_property_type_if_present(entity_definition, prop, type):
    if prop in entity_definition:
        stringified_type = _type_to_string(type)
        if not _type_is_correct(entity_definition[prop], type):
            return ['The property "{}" must be a {}!'.format(prop, stringified_type)]


def _unique_pattern_tokens(entity_definition):
    patterns = entity_definition['patterns'] if 'patterns' in entity_definition else []
    return set([token for pattern in patterns for token_slot in pattern for token in token_slot])


def _unique_extra_tokens(entity_definition):
    if 'extraTokens' not in entity_definition:
        return set()

    return set([token['label'] for token in entity_definition['extraTokens']])


def _type_to_string(type):
    if type == 'function':
        return 'function'
    if type.__name__ == 'str':
        return 'string'
    else:
        return type.__name__


def _type_is_correct(item, type):
    if type == 'function':
        return isfunction(item)
    else:
        return isinstance(item, type)


VALIDATION_FUNCTIONS = [
    _entity_definition_is_dictionary,
    _validate_patterns_and_extraTokens_properties,
    _validate_extraCleaning,
    _validate_spacing,
    _validate_ontological_tags,
    _validate_entityCleaning,
    _validate_entityValidation,
    _validate_collapsiblePatterns,
]


def find_errors_in_entity_definition(entity_definition, validation_functions=VALIDATION_FUNCTIONS):
    ''' Accumulates a list of errors to return to the user.
    '''
    errors = []
    for func in validation_functions:
        # Minor errors are returned as strings and added to the list.
        # Major errors raise an exception to short circuit the error checking and return errors early.
        try:
            error = func(entity_definition)
            if error:
                # errors returned as lists
                errors += error
        except Exception as e:
            errors.append(str(e))
            break
    return errors
