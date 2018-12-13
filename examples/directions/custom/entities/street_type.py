'''
This contains the entity definition for types of streets.
'''
try:
  from cleaning_functions import capitalize
except ImportError:
  from .cleaning_functions import capitalize

STREET_TYPE = {
  'label':
    'STREET_TYPE',
  'values':
    (
      'alley', 'avenue', 'street', 'boulevard', 'way', 'ave', 'place', 'highway', 'lane', 'drive', 'route', 'square',
      'road', 'expressway'
    )
}

STREET_TYPE_PATTERN = [[['STREET_TYPE']]]

ENTITY_DEFINITION = {
  'patterns': STREET_TYPE_PATTERN,
  'extraTokens': (STREET_TYPE,),
  'extraCleaning': {
    'STREET_TYPE': capitalize,
  }
}
