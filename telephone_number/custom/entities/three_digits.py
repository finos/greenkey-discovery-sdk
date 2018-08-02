'''
This contains the entity definition for three contiguous numbers.
This would be useful for something like a phone number area code.
 '''

THREE_DIGIT_PATTERN = [[['NUM'], ['NUM'], ['NUM']]]

ENTITY_DEFINITION = {
  'patterns': THREE_DIGIT_PATTERN,
  'spacing': {
    'default': '',
  }
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
