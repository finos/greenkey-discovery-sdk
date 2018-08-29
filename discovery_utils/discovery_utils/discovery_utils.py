#!/usr/bin/python
'''
Utility functions for discovery
'''
from __future__ import print_function
from inspect import isfunction


def json_utf_8_encoding(input):
    '''returns json file with utf-8 encoded strings, not unicode. Important for regex stuff '''
    if isinstance(input, dict):
        return {json_utf_8_encoding(key): json_utf_8_encoding(value) for key, value in input.iteritems()}

    if isinstance(input, list):
        return [json_utf_8_encoding(element) for element in input]

    if isinstance(input, unicode):
        return input.encode('utf-8')

    return input


class EntityDefinitionValidator:
    '''
    Initialize this class with an entity definition dictionary.
    The class will throw an exception on initialization if there are any problems with the definition.
    '''

    def __init__(self, entity_definition, entity_name=''):
        self.entity_definition = entity_definition
        self.entity_name = entity_name
        self.validate_entity_definition()
        self.notify_of_success()

    def notify_of_success(self):
        entity_label = '' if not self.entity_name else ' for {}.py'.format(self.entity_name)
        print('Checking entity definition{0:.<35} No errors!'.format(entity_label))

    def validate_entity_definition(self):
        self._entity_definition_is_dictionary()
        self._patterns_property_exists()
        self._patterns_property_has_correct_value()
        self._validate_extraTokens()
        self._validate_extra_tokens_and_pattern_tokens()
        self._validate_extraCleaning()
        self._do_simple_type_checks()
        self._validate_collapsiblePatterns()

    def _entity_definition_is_dictionary(self):
        self._type_check_with_message(self.entity_definition, dict, "Your ENTITY_DEFINITION must be a dictionary!")

    def _patterns_property_exists(self):
        self._property_exists_in_entity_definition('patterns')

    def _patterns_property_has_correct_value(self):
        pattern_error_message = 'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists ' + \
                                'of strings. e.g. [[["NUM"], ["LETTER"]]]'

        self._type_check_with_message(self.entity_definition['patterns'], list, pattern_error_message)

        for pattern in self.entity_definition['patterns']:
            self._type_check_with_message(pattern, list, pattern_error_message)
            for token_slot in pattern:
                self._type_check_with_message(token_slot, list, pattern_error_message)
                for token in token_slot:
                    self._type_check_with_message(token, str, pattern_error_message)

    def _validate_extraTokens(self):
        self._validate_type_if_present('extraTokens', tuple)

    def _validate_extra_tokens_and_pattern_tokens(self):
        pattern_tokens = self._unique_pattern_tokens()
        extra_tokens = self._unique_extra_tokens()

        for token in extra_tokens:
            self._property_exists(
                pattern_tokens, token,
                'The token {} is defined in "extraTokens" but is not used in any "patterns"'.format(token)
            )
        built_in_tokens = ("NUM", "LETTER", "NUM_ORD", "NUM_PLURAL", "TIME_MONTH", "TIME_DAY", "TIME_WEEK")
        for token in pattern_tokens:
            if token not in extra_tokens and token not in built_in_tokens:
                raise Exception(
                    'The token \"{0}\" is used in "patterns" but is not a built in token, '
                    'please define \"{0}\" in "extraTokens"'.format(token)
                )

    def _validate_extraCleaning(self):
        self._validate_type_if_present('extraCleaning', dict)
        if 'extraCleaning' in self.entity_definition:
            for token in self.entity_definition['extraCleaning']:
                self._type_check_with_message(
                    self.entity_definition['extraCleaning'][token], 'function',
                    'Each property in "extraCleaning" must be a function!'
                )

    def _do_simple_type_checks(self):
        self._validate_type_if_present('spacing', dict)
        self._validate_type_if_present('ontological_tags', bool)
        self._validate_type_if_present('entityCleaning', 'function')
        self._validate_type_if_present('entityValidation', 'function')

    def _validate_collapsiblePatterns(self):
        collapsible_pattern_message = 'The "collapsiblePatterns" property must be a tuple of tuples!'
        self._validate_type_if_present('collapsiblePatterns', tuple)
        if 'collapsiblePatterns' in self.entity_definition:
            for collapsible_pattern in self.entity_definition['collapsiblePatterns']:
                self._type_check_with_message(collapsible_pattern, tuple, collapsible_pattern_message)

    def _property_exists_in_entity_definition(self, property):
        return self._property_exists(
            self.entity_definition, property, 'Your ENTITY_DEFINITION must contain a "{}" property!'.format(property)
        )

    def _validate_type_if_present(self, prop, type):
        if prop in self.entity_definition:
            stringified_type = self._type_to_string(type)
            return self._type_check_with_message(
                self.entity_definition[prop], type, 'The property "{}" must be a {}!'.format(prop, stringified_type)
            )

    def _unique_pattern_tokens(self):
        return set(
            [token for pattern in self.entity_definition['patterns'] for token_slot in pattern for token in token_slot]
        )

    def _unique_extra_tokens(self):
        if 'extraTokens' not in self.entity_definition:
            return set()

        for token in self.entity_definition['extraTokens']:
            self._validate_token_of_extraTokens(token)

        return set([token['label'] for token in self.entity_definition['extraTokens']])

    def _validate_token_of_extraTokens(self, token):
        self._type_check_with_message(token, dict, 'Your "extraTokens" must be a tuple of dictionaries!')
        self._property_exists(token, 'label', 'Your "extraTokens" dictionaries must contain a "label" property!')
        self._property_exists(token, 'values', 'Your "extraTokens" dictionaries must contain a "values" property!')

    def _alert_user_of_problem(self, message):
        raise Exception('Error in {}.py'.format(self.entity_name), message)

    def _property_exists(self, struct, prop, message):
        if prop not in struct:
            self._alert_user_of_problem(message)

    def _type_to_string(self, type):
        if type == 'function':
            return 'function'
        if type.__name__ == 'str':
            return 'string'
        else:
            return type.__name__

    def _type_check_with_message(self, item, type, message):
        valid = False
        if type == 'function':
            valid = isfunction(item)
        else:
            valid = isinstance(item, type)
        if not valid:
            self._alert_user_of_problem(message)
