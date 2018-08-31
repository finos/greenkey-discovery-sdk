import pytest
import sys
import json

from discovery_sdk_utils import json_utf_8_encoding, find_errors_in_entity_definition


def test_json_utf_8_encoding():
    json_obj = '''{
      "prop2": {
        "nested_prop": [
          "array",
          "values"
        ]
      },
      "prop": "val"
    }'''
    dict_obj = json.loads(json_obj)
    de_unicoded_dict_obj = json_utf_8_encoding(dict_obj)
    print(de_unicoded_dict_obj)
    assert all(isinstance(key, str) for key in de_unicoded_dict_obj.keys())
    assert all(isinstance(key, str) for key in de_unicoded_dict_obj['prop2'].keys())
    assert all(isinstance(key, str) for key in de_unicoded_dict_obj['prop2']['nested_prop'])


class TestEntityDefinitionValidator(object):

    def test_entity_definition_is_dictionary(self):
        entity_definition = 'this is a string'
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Your ENTITY_DEFINITION must be a dictionary!']

    def test_patterns_property_exists(self):
        entity_definition = {'missing': 'keys'}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Your ENTITY_DEFINITION must contain a "patterns" property!']

    def test_patterns_property_has_correct_value(self):
        entity_definition = {'patterns': 'wrong stuff'}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == [
            'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists of strings. e.g. [[["NUM"], ["LETTER"]]]'
        ]

    def test_patterns_property_has_correct_value_2(self):
        entity_definition = {'patterns': ['wrong stuff']}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == [
            'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists of strings. e.g. [[["NUM"], ["LETTER"]]]'
        ]

    def test_patterns_property_has_correct_value_3(self):
        entity_definition = {'patterns': [['still wrong stuff']]}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == [
            'The "patterns" property of ENTITY_DEFINITION must be a list of lists of lists of strings. e.g. [[["NUM"], ["LETTER"]]]'
        ]

    def test_patterns_property_has_correct_value_valid(self):
        # this finally has a correct patterns value
        entity_definition = {'patterns': [[['NUM']]]}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == []

    def test_validate_extraTokens(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': 'defined_wrong'}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "extraTokens" must be a tuple!']

    def test_validate_extraTokens_2(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ['defined_wrong']}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "extraTokens" must be a tuple!']

    def test_validate_extra_tokens_and_pattern_tokens(self):
        entity_definition = {'patterns': [[['what_am_i']]]}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == [
            'The token "what_am_i" is used in "patterns" but is not a built in token, please define "what_am_i" in "extraTokens"'
        ]

    def test_validate_extra_tokens_and_pattern_tokens_2(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ('defined_wrong',)}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Your "extraTokens" must be a tuple of dictionaries!']

    def test_validate_extra_tokens_and_pattern_tokens_3(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ({'label': 'defined_wrong'},)}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Your "extraTokens" dictionaries must contain a "values" property!']

    def test_validate_extra_tokens_and_pattern_tokens_4(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ({'values': ('defined_wrong')},)}
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Your "extraTokens" dictionaries must contain a "label" property!']

    def test_validate_extra_tokens_and_pattern_tokens_5(self):
        entity_definition = {
            'patterns': [[['defined_wrong']]],
            'extraTokens': ({
                'label': 'correctly',
                'values': ('defined')
            },)
        }
        errors = find_errors_in_entity_definition(entity_definition)
        expected_errors = [
            'The token "correctly" is defined in "extraTokens" but is not used in any "patterns"',
            'The token "defined_wrong" is used in "patterns" but is not a built in token, '
            'please define "defined_wrong" in "extraTokens"'
        ]
        assert errors == expected_errors

    def test_validate_extra_tokens_and_pattern_tokens_6(self):
        # this function should finally pass
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },)
        }
        assert [] == find_errors_in_entity_definition(entity_definition)

    def test_validate_extraCleaning(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'extraCleaning': ''
        }
        assert ['The property "extraCleaning" must be a dict!'] == find_errors_in_entity_definition(entity_definition)

    def test_validate_extraCleaning_2(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'extraCleaning': {
                'NUM': ''
            }
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['Each property in "extraCleaning" must be a function!']

    def test_do_symbol_type_checks_spacing(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'spacing': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "spacing" must be a dict!']

    def test_do_symbol_type_checks_ontological_tags(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'ontological_tags': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "ontological_tags" must be a bool!']

    def test_do_symbol_type_checks_entityCleaning(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'entityCleaning': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "entityCleaning" must be a function!']

    def test_do_symbol_type_checks_entityValidation(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'entityValidation': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "entityValidation" must be a function!']

    def test_validate_collapsiblePatterns(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'collapsiblePatterns': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == ['The property "collapsiblePatterns" must be a tuple!']

    def test_validate_many_errors(self):
        entity_definition = {
            'patterns': [[['defined_wrong']]],
            'extraTokens': ({
                'label': 'correctly',
                'values': ('defined')
            },),
            'extraCleaning': {
                'NUM': ''
            },
            'spacing': '',
            'entityValidation': '',
            'collapsiblePatterns': '',
            'entityCleaning': '',
            'ontological_tags': ''
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == [
            'The token "correctly" is defined in "extraTokens" but is not used in any "patterns"',
            'The token "defined_wrong" is used in "patterns" but is not a built in token, '
            'please define "defined_wrong" in "extraTokens"', 'Each property in "extraCleaning" must be a function!',
            'The property "spacing" must be a dict!', 'The property "ontological_tags" must be a bool!',
            'The property "entityCleaning" must be a function!', 'The property "entityValidation" must be a function!',
            'The property "collapsiblePatterns" must be a tuple!'
        ]

    def test_valid_definition(self):

        def dumb_function(arg):
            return arg

        def dumb_validator(arg):
            return True

        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'extraCleaning': {
                'DEFINED_CORRECT': dumb_function
            },
            'spacing': {
                'NUM': '',
                'NUM_ORD': '',
                'default': ' ',
            },
            'ontological_tags': False,
            'entityCleaning': dumb_function,
            'entityValidation': dumb_validator,
            'collapsiblePatterns': (),
        }
        errors = find_errors_in_entity_definition(entity_definition)
        assert errors == []

    def test_importing_address_number(self):
      import sys
      from importlib import import_module
      sys.path.append('../examples/directions/custom/entities')
      entity = 'address_number.py'

      entity_name = entity.split("/")[-1].replace(".py", "")
      entity_module = import_module(entity_name)

      if 'ENTITY_DEFINITION' in dir(entity_module):
          errors = find_errors_in_entity_definition(entity_module.ENTITY_DEFINITION)
          assert errors == []


if __name__ == '__main__':
    pytest.main(sys.argv)
