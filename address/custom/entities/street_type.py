''' this contians the entity definition for a us license plate '''
# Each interpreter needs a list of patterns to look for

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
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
