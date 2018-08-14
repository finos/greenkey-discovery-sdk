''' this contians the entity definition for a us license plate '''
# Each interpreter needs a list of patterns to look for

ADDRESS_NUMBER_PATTERN = []

ADDRESS_NUMBER_PATTERN = [[['NUM'] for _ in range(i)] for i in range(1, 6)]

ENTITY_DEFINITION = {
  'patterns': ADDRESS_NUMBER_PATTERN,
  'spacing': {
    'NUM': '',
  }
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
