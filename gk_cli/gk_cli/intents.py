from __future__ import print_function

import json
import doctest
from PyInquirer import prompt
from style import style
from cli_utils import format_file_name

intent_label_prompt = [
    {
        'type': 'input',
        'message':
            'What would you like to name your intent? '
            '(intent names are all lowercase and underscore separated by convention)',
        'name': 'value'
    }
]

examples_prompt = [
    {
        'type': 'list',
        'message': 'Would you like to add example sentences so that discovery can automatically detect your intent?',
        'name': 'value',
        'choices': [
            {
                'name': 'Yes, this intent will have example sentences.'
            },
            {
                'name': 'No, I do not need them.'
            },
        ],
    }
]

example_sentence_prompt = [
    {
        'type': 'input',
        'message':
            'Please type an example sentence for this intent. (Type "help" for assistance).',
        'name': 'value'
    }
]


additional_examples = [
    {
        'type': 'list',
        'message': 'Do you need any additional examples for this intent?',
        'name': 'value',
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

additional_custom_intents = [
    {
        'type': 'list',
        'message': 'Do you need any additional intents for your project?',
        'name': 'value',
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


def create_new_intent_definition_file(file_location):
    print(
        'First, we will add in the "intents" one at a time. '
    )
    intent_definitions_array = _recursively_add_intent_definitions([])
    intent_config_data = {'intents': intent_definitions_array}
    file_name = "{}intents.json".format(file_location)

    with open(file_name, 'w') as f:
        json.dump(intent_config_data, f, indent=4)
        print('Successfully created intents.json file.')

    import pprint
    pp = pprint.PrettyPrinter(indent=4, width=180).pprint
    pp(intent_config_data)


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
    return intent_definition


def _user_will_use_examples():
  user_needs_examples = prompt(examples_prompt, style=style)
  return user_needs_examples['value'] == 'Yes, this intent will have example sentences.'


def _get_intent_label():
    token_name = prompt(intent_label_prompt, style=style)
    return format_file_name(token_name['value'])


def _recursively_get_intent_examples(example_sentences=[]):
    example_sentence = _prompt_user_for_example()
    example_sentences.append(example_sentence)
    if _user_needs_another_example():
        return _recursively_get_intent_examples(example_sentences)
    return example_sentences


def _user_needs_another_example():
    response = prompt(additional_examples, style=style)
    return response['value'] == 'Yes'


def _prompt_user_for_example():
    example = prompt(example_sentence_prompt, style=style)
    if example['value'].lower().strip() == 'help':
      print(
        'Your example sentence should demonstrate the kinds of things a user would say in a typical use case. '
        'You can specify special words that will be filled in later with entity definitions by typing them '
        'in curly braces. '
        'For example, you could type the sentence "Turn right onto {street_name}, '
        'and Discovery will know to look for sentences with a similar structure that are populated with street names. '
        'For the previous example to work, you would have to make a matching entity definition '
        'for an entity labeled "street_name".'
      )
      return _prompt_user_for_example()
    return example['value']


def _user_needs_another_intent():
    add_another_intent = prompt(additional_custom_intents, style=style)
    return add_another_intent['value'] == 'Yes'


if __name__ == '__main__':
    doctest.testmod(raise_on_error=False)
