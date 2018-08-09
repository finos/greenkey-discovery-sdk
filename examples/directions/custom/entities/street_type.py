'''
This contains the entity definition for types of streets.
'''

from cleaning_functions import capitalize

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

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
