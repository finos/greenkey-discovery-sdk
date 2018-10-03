from __future__ import print_function, absolute_import, unicode_literals

import string
import doctest
from PyInquirer import prompt, Validator, ValidationError
from gk_cli.style import style


def raise_error_for_blank_doc(document):
  if document.text.strip() == '':
      raise ValidationError(
          message='Oops, you entered a blank response, please try again!',
          cursor_position=len(document.text))  # Move cursor to end


class BlankAnswerValidator(Validator):
    def validate(self, document):
      raise_error_for_blank_doc(document)


class ListOfSingleWordsValidator(Validator):
    def validate(self, document):
        raise_error_for_blank_doc(document)
        words = document.text.split(',')
        for word in words:
            if ' ' in word.strip():
                raise ValidationError(
                    message='Oops, you must only enter single words! "{}" has a space!'.format(word),
                    cursor_position=len(document.text))  # Move cursor to end


def prompt_user(prompt_dict):
  response = prompt(prompt_dict, style=style)
  return response['value']


def prompt_user_with_help_check(prompt_dict, help_message):
  response = prompt_user(prompt_dict)
  if _user_wants_help(response):
    print(help_message)
    return prompt_user_with_help_check(prompt_dict, help_message)
  return response


def format_file_name(file_name):
    '''
    >>> format_file_name("oh Yeah!&&")
    'oh_Yeah'
    '''
    de_quoted_file_name = remove_quotation_marks(file_name)

    valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
    filtered_file_name = ''.join(c for c in de_quoted_file_name if c in valid_chars)

    if ' ' not in filtered_file_name:
        return filtered_file_name

    snake_cased_filename = filtered_file_name.replace(' ', '_')
    return snake_cased_filename


def remove_quotation_marks(string):
  '''
  >>> string = "'That\\'s just great'"
  >>> remove_quotation_marks(string)
  "That's just great"
  >>> string = '"That\\'s just great"'
  >>> remove_quotation_marks(string)
  "That's just great"
  '''
  return string.replace('"', '').strip("\'")


def _user_wants_help(string):
  '''
  >>> string = "Help "
  >>> _user_wants_help(string)
  True
  '''
  cleaned_response = remove_quotation_marks(string).lower().strip()
  return cleaned_response == 'help'


if __name__ == '__main__':
  doctest.testmod(raise_on_error=False)
