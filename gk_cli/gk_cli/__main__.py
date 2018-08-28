from __future__ import print_function

import os
import re
from PyInquirer import prompt
from style import style
from entity import create_new_entity
from intents import create_new_intent_definition_file

create_type = [
    {
        'type': 'list',
        'message': 'What would you like to do?',
        'name': 'value',
        'choices': [
            {
                'name': 'Create a new entity'
            },
            {
                'name': 'Create a new project'
            },
        ],
    }
]

create_entities_folder = [
    {
        'type':
            'list',
        'message':
            'There is no "entities" folder in the current working directory. '
            'Would you like to create one for your new entity?',
        'name':
            'value',
        'choices': [
            {
                'name': 'Yes, create an "entities" folder.'
            },
            {
                'name': 'No, I will make one later.'
            },
        ],
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
        'name': 'value'
    }
]


def prompt_for_initial_action():
    option = prompt(create_type, style=style)
    return option['value']


def user_wants_a_new_entities_directory():
    response = prompt(create_entities_folder, style=style)
    return response['value'] == 'Yes, create an "entities" folder.'


def decision_about_custom_folder():
    response = prompt(create_custom_folder, style=style)
    return response['value']


def create_new_entity_in_folder(file_path, entity_name=None):
  # and entities directory is found
  if os.path.isdir(file_path + "entities"):
      create_new_entity(file_path + 'entities/', entity_name)
  # we are currently in an entities directory
  elif os.getcwd().endswith(file_path + 'entities'):
      create_new_entity(file_path + '', entity_name)

  elif user_wants_a_new_entities_directory():
      os.makedirs(file_path + 'entities')
      print('\n***Created new directory entities to use for entity definition files.***')
      create_new_entity(file_path + 'entities/', entity_name)

  else:
      print(
          'The new entity definition will be created in this directory. '
          'You will need to move this file into a directory labeled "entities" '
          'before Discovery will be able to use it.'
      )
      create_new_entity(file_path + '', entity_name)


def main():
    option = prompt_for_initial_action()
    if option == 'Create a new entity':
        create_new_entity_in_folder('')

    else:
        # if custom directory is found
        if os.path.isdir("custom"):
            return create_new_project('custom/')
        # we are currently in an custom directory
        elif os.getcwd().endswith('custom'):
            return create_new_project('')

        custom_folder = decision_about_custom_folder()
        if custom_folder == 'Yes, create a "custom" folder.':
            os.makedirs('custom')
            print('\n***Created new directory "custom" to use for Discovery mount directory.***')
            create_new_project('custom/')

        elif custom_folder == 'No, I want to name my mount volume something other than "custom."':
            name_of_mount_volume = get_name_of_custom_mount_volume()
            create_new_project(name_of_mount_volume)
        else:
            create_new_project('')


def create_new_project(file_location):
    create_new_intent_definition_file(file_location)
    created_entities = check_for_created_entities(file_location)
    if len(created_entities):
      print('The following entities were discovered:')
      for entity in created_entities:
        print(entity)
      for entity in created_entities:
        create_new_entity_in_folder(file_location, entity)


def get_name_of_custom_mount_volume():
    response = prompt(name_of_mount_volume, style=style)
    if response['value'].lower().strip() == 'ls':
        for dir in list(os.walk('.'))[0][1]:
            print(dir)
        return get_name_of_custom_mount_volume()
    if not os.path.isdir(response['value']):
        os.makedirs(response['value'])
        print('\n***Created new directory {} to use for Discovery mount directory.***'.format(response['value']))
    if not response['value'].endswith('/'):
        response['value'] += '/'
    return response['value']


ENTITY_REGEX = re.compile(r'\{(\w*)\}')


def check_for_created_entities(file_location):
    entities = set()
    with open(file_location + 'intents.json') as f:
        data = f.read()
        entities.update(ENTITY_REGEX.findall(data))
    return entities


if __name__ == '__main__':
    main()
