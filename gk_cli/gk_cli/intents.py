from __future__ import print_function, absolute_import, unicode_literals

import json
import doctest
from gk_cli.cli_utils import (
    BlankAnswerValidator, format_file_name, ListOfSingleWordsValidator, prompt_user, prompt_user_with_help_check
)

intent_label_prompt = [
    {
        'type': 'input',
        'message': 'What would you like to name your intent? '
                   '(Type "help" for assistance)',
        'name': 'value',
        'validate': BlankAnswerValidator,
        'filter': format_file_name,
    }
]

example_sentences = [
    {
        'type': 'confirm',
        'message': 'Would you like to add example sentences so that discovery can automatically detect your intent?',
        'name': 'value',
    }
]

entities_list = [
    {
        'type': 'confirm',
        'message': 'Would you like to add a list of entities for Discovery to find?',
        'name': 'value',
    }
]

example_sentence_prompt = [
    {
        'type': 'input',
        'message': 'Please type an example sentence for this intent. (Type "help" for assistance).',
        'name': 'value',
        'validate': BlankAnswerValidator,
    }
]

additional_examples = [
    {
        'type': 'confirm',
        'message': 'Do you need any additional examples for this intent?',
        'name': 'value',
    }
]

additional_custom_intents = [
    {
        'type': 'confirm',
        'message': 'Do you need any additional intents for your project?',
        'name': 'value',
    }
]


def generate_entities_list_prompt(intent_name):
    return [
        {
            'type': 'input',
            'message':
                'Enter your comma-separated list of entites for your intent "{}" '
                '(Type "help" for assistance)'.format(intent_name),
            'name': 'value',
            'validate': ListOfSingleWordsValidator,
        }
    ]


def create_new_intent_definition_file(file_location):
    print('First, we will add in the "intents" one at a time. ')
    intent_definitions_array = _recursively_add_intent_definitions([])
    intent_config_data = {'intents': intent_definitions_array}
    file_name = "{}intents.json".format(file_location)

    with open(file_name, 'w') as f:
        json.dump(intent_config_data, f, indent=4)
        print('\n*** Successfully created intents.json file. ***\n')

    return intent_config_data


def _recursively_add_intent_definitions(intent_definitions=[]):
    new_intent_definition = _get_custom_intent_definition()
    intent_definitions.append(new_intent_definition)
    if _user_needs_another_intent():
        return _recursively_add_intent_definitions(intent_definitions)
    return intent_definitions


def _get_custom_intent_definition():
    intent_definition = {}
    intent_definition['label'] = _get_intent_label()
    if _user_will_use_examples():
        intent_definition['examples'] = _recursively_get_intent_examples([])
    elif _user_will_use_entities_list():
        intent_definition['entities'] = _get_entities(intent_definition['label'])
    return intent_definition


def _user_will_use_examples():
    return prompt_user(example_sentences)


def _user_will_use_entities_list():
    return prompt_user(entities_list)


def _get_entities(intent_name):
    entities_list_prompt = generate_entities_list_prompt(intent_name)
    help_message = (
        '\nEnter in at least one entity name. '
        'If you have multiple entities, separate them by commas. '
        'Only single words will be allowed for entity labels. '
        'Camel case your entity names. '
        'For example: "food_item, drink_item"\n'
    )
    response = prompt_user_with_help_check(entities_list_prompt, help_message)
    return [entity.strip() for entity in response.split(',')]


def _get_intent_label():
    help_message = (
        '\nAn "intent" is a classification for a transcript. '
        'Your intent should summarize the kind of transcript you would like to analyze. '
        'Intent names are all lowercase and underscore separated by convention '
        '(e.g. "request_for_directions" or "food_order"). '
        'You do not need quotation marks in your response.\n'
    )
    return prompt_user_with_help_check(intent_label_prompt, help_message)


def _recursively_get_intent_examples(example_sentences=[]):
    example_sentence = _prompt_user_for_example()
    example_sentences.append(example_sentence)
    if _user_needs_another_example():
        return _recursively_get_intent_examples(example_sentences)
    return example_sentences


def _user_needs_another_example():
    return prompt_user(additional_examples)


def _prompt_user_for_example():
    help_message = (
        '\nYour example sentence should demonstrate the kinds of things a user would say in a typical use case. '
        'You can specify special words that will be filled in later with entity definitions by typing them '
        'in curly braces. '
        'For example, you could type the sentence "Turn right onto {street_name}", '
        'and Discovery will know to look for sentences with a similar structure that are populated with street names. '
        'For the previous example to work, you would have to make a matching entity definition '
        'for an entity labeled "street_name". You do not need quotation marks in your response.\n'
    )
    return prompt_user_with_help_check(example_sentence_prompt, help_message)


def _user_needs_another_intent():
    return prompt_user(additional_custom_intents)


if __name__ == '__main__':
    doctest.testmod(raise_on_error=False)
