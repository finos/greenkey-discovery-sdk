''' this contians the entity definition for a us license plate '''
# Each interpreter needs a list of patterns to look for


DIRECTION = {
  'label': 'DIRECTION',
  'values': ('north', 'south', 'east', 'west'),
}

ADDRESS_NUMBER_PATTERN = [[['DIRECTION']]]

ENTITY_DEFINITION = {
  'patterns': ADDRESS_NUMBER_PATTERN,
  'extraTokens': (DIRECTION,),
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
