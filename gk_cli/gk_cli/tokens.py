from __future__ import print_function

import doctest
from cli_utils import (
    BlankAnswerValidator, format_file_name, ListOfSingleWordsValidator, prompt_user, prompt_user_with_help_check
)


def _format_token_name(token_name):
    '''
    >>> _format_token_name("the Best.,")
    'THE_BEST'
    '''
    token_name = format_file_name(token_name)
    return token_name.upper()


def _generate_custom_tokens_prompt(entity_name):
    return [
        {
            'type':
                'list',
            'message':
                'Do you need any custom tokens for your entity "{}"?'.format(entity_name),
            'name':
                'value',
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
        'type': 'confirm',
        'message': 'Do you need any additional custom tokens for your entity?',
        'name': 'value',
    }
]

token_label_prompt = [
    {
        'type': 'input',
        'message': 'What would you like to name your token? '
                   '(Type "help" for assistance)',
        'name': 'value',
        'validate': BlankAnswerValidator,
        'filter': _format_token_name,
    }
]


def generate_token_values_prompt(token_name):
    return [
        {
            'type': 'input',
            'message':
                'Enter your comma-separated list of token values for your token "{}" '
                '(Type "help" for assistance)'.format(token_name),
            'name': 'value',
            'validate': ListOfSingleWordsValidator,
        }
    ]


def get_custom_tokens(entity_name):
    custom_token_definitions = []
    entity_has_custom_tokens = _prompt_for_custom_tokens(entity_name)
    if entity_has_custom_tokens:
        custom_token_definitions = _recursively_add_token_definitions(custom_token_definitions)
    return custom_token_definitions


def _prompt_for_custom_tokens(entity_name):
    custom_tokens_prompt = _generate_custom_tokens_prompt(entity_name)
    help_message = (
        '\nA "token" is a way of classifying a type of word in a transcript. '
        'Discovery comes with some built in tokens for commonly used word types like numbers and letters. '
        'If you have a special type of word that you would like discovery to find, '
        'you should make a custom token for each category of word that you are looking for. '
        'If you make a custom token, you will first be prompted for a label for your token, '
        'and next you will be prompted for a list of the actual words that discovery should find.\n'
    )
    response = prompt_user_with_help_check(custom_tokens_prompt, help_message)
    return response == 'Yes'


def _recursively_add_token_definitions(token_definitions=[]):
    new_token_definition = _get_custom_token_definition()
    token_definitions.append(new_token_definition)
    if _user_needs_another_token():
        return _recursively_add_token_definitions(token_definitions)
    return token_definitions


def _get_custom_token_definition():
    token_definition = {}
    token_definition['label'] = _get_token_label()
    token_definition['values'] = _get_token_values(token_definition['label'])
    return token_definition


def _get_token_label():
    help_message = (
        '\nToken names are a label for a list of words. '
        'Token names are all uppercase and underscore separated by convention.\n'
    )
    response = prompt_user_with_help_check(token_label_prompt, help_message)
    return response.encode('utf-8')


def _get_token_values(token_name):
    token_values_prompt = generate_token_values_prompt(token_name)
    help_message = (
        '\nEnter in at least one word for your token definition. '
        'If you have multiple words, separate them by commas. '
        'Only single words will be allowed. '
        'For example, entering "pizza, pasta, bread" is valid, '
        'but "spaghetti with meatballs, pasta alfredo" is not.\n'
    )
    response = prompt_user_with_help_check(token_values_prompt, help_message)
    return tuple([value.strip().encode('utf-8') for value in response.split(',')])


def _user_needs_another_token():
    return prompt_user(additional_custom_tokens)


if __name__ == '__main__':
    doctest.testmod(raise_on_error=False)
