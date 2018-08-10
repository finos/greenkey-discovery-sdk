''' this contians the entity definition for a us license plate '''
# Each interpreter needs a list of patterns to look for

TRANSPORTATION_METHOD = {
  'label': 'TRANSPORTATION_METHOD',
  'values': (
    'foot',
    'walk',
    'walking',
    'bicycle',
    'bike',
    'bus',
    'train',
    'car',
  )
}

TRANSPORTATION_PATTERNS = [[['TRANSPORTATION_METHOD']]]

ENTITY_DEFINITION = {
  'extraTokens': (TRANSPORTATION_METHOD,),
  'patterns': TRANSPORTATION_PATTERNS,
}
