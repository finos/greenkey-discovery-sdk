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
