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
