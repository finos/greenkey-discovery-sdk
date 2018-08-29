import pytest
import sys
import json

from discovery_utils.discovery_utils import json_utf_8_encoding, EntityDefinitionValidator


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
        with pytest.raises(Exception, match=r'dictionary'):
            EntityDefinitionValidator(entity_definition)

    def test_patterns_property_exists(self):
        entity_definition = {'missing': 'keys'}
        with pytest.raises(Exception, match=r'patterns'):
            EntityDefinitionValidator(entity_definition)

    def test_patterns_property_has_correct_value(self):
        entity_definition = {'patterns': 'wrong stuff'}
        with pytest.raises(Exception, match=r'list of lists of lists of strings'):
            EntityDefinitionValidator(entity_definition)

    def test_patterns_property_has_correct_value_2(self):
        entity_definition = {'patterns': ['wrong stuff']}
        with pytest.raises(Exception, match=r'list of lists of lists of strings'):
            EntityDefinitionValidator(entity_definition)

    def test_patterns_property_has_correct_value_3(self):
        entity_definition = {'patterns': [['still wrong stuff']]}
        with pytest.raises(Exception, match=r'list of lists of lists of strings'):
            EntityDefinitionValidator(entity_definition)

    def test_patterns_property_has_correct_value_valid(self):
        # this finally has a correct patterns value
        entity_definition = {'patterns': [[['NUM']]]}
        EntityDefinitionValidator(entity_definition)

    def test_validate_extraTokens(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': 'defined_wrong'}
        with pytest.raises(Exception, match=r'must be a tuple'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extraTokens_2(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ['defined_wrong']}
        with pytest.raises(Exception, match=r'must be a tuple'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens(self):
        entity_definition = {'patterns': [[['what_am_i']]]}
        with pytest.raises(Exception, match=r'not a built in token'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens_2(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ('defined_wrong',)}
        with pytest.raises(Exception, match=r'must be a tuple of dictionaries'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens_3(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ({'label': 'defined_wrong'},)}
        with pytest.raises(Exception, match=r'must contain a "values"'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens_4(self):
        entity_definition = {'patterns': [[['defined_wrong']]], 'extraTokens': ({'values': ('defined_wrong')},)}
        with pytest.raises(Exception, match=r'must contain a "label"'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens_5(self):
        entity_definition = {
            'patterns': [[['defined_wrong']]],
            'extraTokens': ({
                'label': 'correctly',
                'values': ('defined')
            },)
        }
        with pytest.raises(Exception, match=r'not used in any "patterns"'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_extra_tokens_and_pattern_tokens_6(self):
        # this function should finally pass
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },)
        }
        assert EntityDefinitionValidator(entity_definition)

    def test_validate_extraCleaning(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'extraCleaning': ''
        }
        with pytest.raises(Exception, match=r'The property "extraCleaning" must be a dict!'):
            EntityDefinitionValidator(entity_definition)

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
        with pytest.raises(Exception, match=r'Each property in "extraCleaning" must be a function!'):
            EntityDefinitionValidator(entity_definition)

    def test_do_symbol_type_checks_spacing(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'spacing': ''
        }
        with pytest.raises(Exception, match=r'The property "spacing" must be a dict!'):
            EntityDefinitionValidator(entity_definition)

    def test_do_symbol_type_checks_ontological_tags(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'ontological_tags': ''
        }
        with pytest.raises(Exception, match=r'The property "ontological_tags" must be a bool!'):
            EntityDefinitionValidator(entity_definition)

    def test_do_symbol_type_checks_entityCleaning(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'entityCleaning': ''
        }
        with pytest.raises(Exception, match=r'The property "entityCleaning" must be a function!'):
            EntityDefinitionValidator(entity_definition)

    def test_do_symbol_type_checks_entityValidation(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'entityValidation': ''
        }
        with pytest.raises(Exception, match=r'The property "entityValidation" must be a function!'):
            EntityDefinitionValidator(entity_definition)

    def test_validate_collapsiblePatterns(self):
        entity_definition = {
            'patterns': [[['DEFINED_CORRECT']]],
            'extraTokens': ({
                'label': 'DEFINED_CORRECT',
                'values': ('defined')
            },),
            'collapsiblePatterns': ''
        }
        with pytest.raises(Exception, match=r'The property "collapsiblePatterns" must be a tuple!'):
            EntityDefinitionValidator(entity_definition)

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
        EntityDefinitionValidator(entity_definition)


if __name__ == '__main__':
    pytest.main(sys.argv)
