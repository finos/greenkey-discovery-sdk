'''
This Contains the entity definition for four contiguous numbers.
This would be useful for part of a phone number, or a pin number.
'''

FOUR_DIGIT_PATTERN = [[['NUM'], ['NUM'], ['NUM'], ['NUM']]]

ENTITY_DEFINITION = {
  'patterns': FOUR_DIGIT_PATTERN,
  'spacing': {
    'default': '',
  }
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
