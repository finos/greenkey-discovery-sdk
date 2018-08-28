from __future__ import print_function

import doctest
from PyInquirer import prompt
from style import style
from cli_utils import format_file_name
from tokens import get_custom_tokens

entity_name_prompt = [
    {
        'type': 'input',
        'message': 'What would you like to name your entity? (camel case your name)',
        'name': 'value'
    }
]


def create_new_entity(file_location, entity_name_choice=None):
    if entity_name_choice is None:
        entity_name_choice = _prompt_for_entity_name()
    custom_tokens = get_custom_tokens(entity_name_choice)
    _create_new_entity_file(entity_name_choice, custom_tokens, file_location)


def _prompt_for_entity_name():
    entity_name_choice = prompt(entity_name_prompt, style=style)
    entity_name = entity_name_choice['value']

    if entity_name.strip() == '':
        print('You did not type a valid entity name!')
        return _prompt_for_entity_name()

    if ' ' in entity_name:
        print('Spaces are not allowed! Spaces have been converted to underscores.')

    return format_file_name(entity_name)


def _create_new_entity_file(entity_name, custom_tokens, file_location):
    file_name = "{}{}.py".format(file_location, entity_name)
    file_content = _get_file_content(entity_name, custom_tokens)

    with open(file_name, 'w') as f:
        f.write(file_content)
        print('Successfully created entity {}'.format(entity_name))
        pass
    print(entity_name)


def _get_file_content(entity_name, custom_tokens):
    custom_token_content = _get_custom_token_content(custom_tokens)
    entity_patterns_content = _get_entity_patterns_content(entity_name, custom_tokens)
    entity_definition_content = _get_entity_definition_content(entity_name, custom_tokens)
    file_validation_content = '''
if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
'''

    file_content = custom_token_content + \
                   entity_patterns_content + \
                   entity_definition_content + \
                   file_validation_content
    return file_content


def _get_custom_token_content(custom_tokens):
    '''
    >>> custom_tokens = [{'label': 'TEST', 'values': ('one', 'two')}]
    >>> _get_custom_token_content(custom_tokens)
    "TEST = {'values': ('one', 'two'), 'label': 'TEST'}\\n\\n"
    '''
    custom_token_content = ''
    if len(custom_tokens):
        for token in custom_tokens:
            custom_token_content += '{label} = {token}\n'.format(label=token['label'], token=token)
    return custom_token_content + '\n'


def _get_entity_patterns_content(entity_name, custom_tokens):
    '''
    >>> custom_tokens = [{'label': 'TEST', 'values': ('one', 'two')}]
    >>> _get_entity_patterns_content("FUN", custom_tokens)
    "FUN_PATTERNS = [[['TEST']]]\\n"
    >>> _get_entity_patterns_content("FUN", [])
    "# change this to suit your needs. The following pattern would search for one number followed by one letter.\\nFUN_PATTERNS[[['NUM'], ['LETTER']]]\\n\\n"
    '''
    entity_patterns_content = ''
    entity_pattern_label = entity_name.upper() + '_PATTERNS'
    if len(custom_tokens):
        entity_patterns_content = entity_pattern_label + ' = ' + str([[[token['label']]] for token in custom_tokens])
    else:
        entity_patterns_content = '# change this to suit your needs. ' + \
                                  'The following pattern would search for one number followed by one letter.\n' + \
                                  entity_pattern_label + "[[['NUM'], ['LETTER']]]\n"
    return entity_patterns_content + '\n'


def _get_entity_definition_content(entity_name, custom_tokens):
    '''
    >>> custom_tokens = [{'label': 'TEST', 'values': ('one', 'two')}]
    >>> _get_entity_definition_content("FUN", custom_tokens)
    "\\nENTITY_DEFINITION = {\\n  'patterns': FUN_PATTERNS,\\n  'extraTokens': ('TEST',),\\n}\\n\\n"
    '''
    entity_definition_content = '''
ENTITY_DEFINITION = {
  'patterns': ''' + entity_name.upper() + '''_PATTERNS,'''
    if len(custom_tokens):
        entity_definition_content += '''
  'extraTokens': ''' + str(tuple([token['label'] for token in custom_tokens])) + ','
    entity_definition_content += '''
}
'''
    return entity_definition_content + '\n'


if __name__ == '__main__':
    doctest.testmod(raise_on_error=False)
