from __future__ import print_function

import os
import re
from .entity import create_new_entity
from .intents import create_new_intent_definition_file
from .cli_utils import BlankAnswerValidator, format_file_name, prompt_user

create_type = [
    {
        'type': 'list',
        'message': 'What would you like to do?',
        'name': 'value',
        'choices': [
            {
                'name': 'Create a new project.'
            },
            {
                'name': 'Create a new entity for an existing project.'
            },
        ],
    }
]

create_entities_folder = [
    {
        'type':
            'confirm',
        'message':
            'There is no "entities" folder in the current working directory. '
            'Would you like to create one for your new entity?',
        'name':
            'value',
    }
]

create_custom_folder = [
    {
        'type':
            'list',
        'message':
            'There is no "custom" folder in the directory. Would you like to create one for your new entity?',
        'name':
            'value',
        'choices':
            [
                {
                    'name': 'Yes, create a "custom" folder.'
                },
                {
                    'name': 'No, I want to name my mount volume something other than "custom."'
                },
                {
                    'name': 'No, I will make one later.'
                },
            ],
    }
]

name_of_mount_volume = [
    {
        'type': 'input',
        'message':
            'What is the name of the directory you will use as your mounted directory? '
            '(type "ls" to see the directories in your present working directory)',
        'name': 'value',
        'validate': BlankAnswerValidator,
        'filter': format_file_name,
    }
]


def user_wants_a_new_entities_directory():
    return prompt_user(create_entities_folder)


def create_new_entity_in_folder(file_path, entity_name=None):
  # and entities directory is found
  if os.path.isdir(file_path + "entities"):
      create_new_entity(file_path + 'entities/', entity_name)
  # we are currently in an entities directory
  elif os.getcwd().endswith(file_path + 'entities'):
      create_new_entity(file_path + '', entity_name)

  elif user_wants_a_new_entities_directory():
      create_new_entities_folder(file_path)
      create_new_entity(file_path + 'entities/', entity_name)

  else:
      print(
          'The new entity definition will be created in this directory. '
          'You will need to move this file into a directory labeled "entities" '
          'before Discovery will be able to use it.'
      )
      create_new_entity(file_path + '', entity_name)


def create_new_entities_folder(file_path):
  try:
    os.makedirs(file_path + 'entities')
    print('\n*** Created new directory "entities" to use for entity definition files. ***\n')
  except OSError:
    pass


def main():
    option = prompt_user(create_type)
    if option == 'Create a new entity':
        create_new_entity_in_folder('')

    else:
        # if custom directory is found
        if os.path.isdir("custom"):
            return create_new_project('custom/')
        # we are currently in an custom directory
        elif os.getcwd().endswith('custom'):
            return create_new_project('')

        custom_folder = prompt_user(create_custom_folder)
        if custom_folder == 'Yes, create a "custom" folder.':
            os.makedirs('custom')
            print('\n*** Created new directory "custom" to use for Discovery mount directory. ***\n')
            create_new_project('custom/')

        elif custom_folder == 'No, I want to name my mount volume something other than "custom."':
            name_of_mount_volume = get_name_of_custom_mount_volume()
            create_new_project(name_of_mount_volume)
        else:
            create_new_project('')


def create_new_project(file_location):
    intent_config = create_new_intent_definition_file(file_location)
    created_entities = check_for_created_entities(intent_config)
    if len(created_entities):
      create_new_entities_folder(file_location)
      print('The following entities were discovered: ', ', '.join(created_entities))
      for entity in created_entities:
        create_new_entity(file_location + 'entities/', entity)


def get_name_of_custom_mount_volume():
    response = prompt_user(name_of_mount_volume)
    if response.lower().strip() == 'ls':
        for dir in list(os.walk('.'))[0][1]:
            print(dir)
        return get_name_of_custom_mount_volume()
    if not os.path.isdir(response):
        os.makedirs(response)
        print('\n***Created new directory "{}" to use for Discovery mount directory.***\n'.format(response))
    if not response.endswith('/'):
        response += '/'
    return response


ENTITY_REGEX = re.compile(r'\{(\w*)\}')


def check_for_created_entities(intent_config):
    entities = set()
    for intent in intent_config['intents']:
      if 'examples' in intent:
        entities.update(ENTITY_REGEX.findall(' '.join(intent['examples'])))
      elif 'entities' in intent:
        entities.update(intent['entities'])
    return entities


if __name__ == '__main__':
    main()
