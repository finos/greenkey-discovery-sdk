''' This contains the entity definition for a cardinal directions '''
try:
  from cleaning_functions import capitalize
except ImportError:
  from .cleaning_functions import capitalize


DIRECTION = {
  'label': 'DIRECTION',
  'values': ('north', 'south', 'east', 'west'),
}

ADDRESS_NUMBER_PATTERN = [[['DIRECTION']]]

ENTITY_DEFINITION = {
  'patterns': ADDRESS_NUMBER_PATTERN,
  'extraTokens': (DIRECTION,),
  'extraCleaning': {
    'DIRECTION': capitalize,
  }
}
