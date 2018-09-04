from __future__ import print_function

import doctest
from PyInquirer import prompt
from style import style
from cli_utils import format_file_name

custom_tokens = [
    {
        'type':
            'list',
        'message':
            'Do you need any custom tokens for your entity?',
        'name':
            'choice',
        'choices':
            [
                {
                    'name': 'Yes'
                },
                {
                    'name': 'No, the built in tokens are sufficient.'
                },
                {
                    'name': 'I do not know. What is a token?'
                },
            ],
    }
]

additional_custom_tokens = [
    {
        'type': 'list',
        'message': 'Do you need any additional custom tokens for your entity?',
        'name': 'choice',
        'choices': [
            {
                'name': 'Yes'
            },
            {
                'name': 'No'
            },
        ],
    }
]

token_label_prompt = [
    {
        'type':
            'input',
        'message':
            'What would you like to name your token?'
            '(token names are all uppercase and underscore separated by convention)',
        'name':
            'value'
    }
]

token_values_prompt = [
    {
        'type': 'input',
        'message':
            'Enter in at least one word for your token definition. '
            'If you have multiple words, separate them by commas. '
            'Only single words will be allowed. ("right, left" is valid; "turn right, turn left" is not)',
        'name': 'values'
    }
]


def get_custom_tokens(entity_name):
    custom_token_definitions = []
    print('\nGetting tokens for entity {}'.format(entity_name))
    entity_has_custom_tokens = _prompt_for_custom_tokens()
    if entity_has_custom_tokens:
        custom_token_definitions = _recursively_add_token_definitions(custom_token_definitions)
    return custom_token_definitions


def _prompt_for_custom_tokens():
    response = prompt(custom_tokens, style=style)
    if response['choice'] == 'I do not know. What is a token?':
        print(
            'A token is a way of classifying a type of word in a transcript.'
            'Discovery comes with some built in tokens for commonly used word types like numbers and letters.'
            'If you have a special type of word that you would like discovery to find, '
            'you should make a custom token for each category of word that you are looking for.'
            'If you make a custom token, you will first be prompted for a label for your token, '
            'and next you will be prompted for a list of the actual words that discovery should find.'
        )
        return _prompt_for_custom_tokens()
    return response['choice'] == 'Yes'


def _recursively_add_token_definitions(token_definitions=[]):
    new_token_definition = _get_custom_token_definition()
    token_definitions.append(new_token_definition)
    if _user_needs_another_token():
        return _recursively_add_token_definitions(token_definitions)
    return token_definitions


def _get_custom_token_definition():
    token_definition = {}
    token_definition['label'] = _get_token_label()
    token_definition['values'] = _get_token_values()
    return token_definition


def _get_token_label():
    token_name = prompt(token_label_prompt, style=style)
    return _format_token_name(token_name['value']).encode('utf-8')


def _get_token_values():
    response = prompt(token_values_prompt, style=style)
    return tuple([value.encode('utf-8') for value in response['values'].split(',')])


def _user_needs_another_token():
    add_another_token = prompt(additional_custom_tokens, style=style)
    return add_another_token['choice'] == 'Yes'


def _format_token_name(token_name):
    '''
    >>> _format_token_name("the Best.,")
    'THE_BEST'
    '''
    token_name = format_file_name(token_name)
    return token_name.upper()


if __name__ == '__main__':
    doctest.testmod(raise_on_error=False)
