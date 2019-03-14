''' this contians the entity definition for an address number '''
# Each interpreter needs a list of patterns to look for

from nlp.cleanText import text2int

ZERO = {
  'label': 'ZERO',
  'values': (
    'o',
    'oh',
    'zero',
  )
}

ADDRESS_NUMBER_PATTERN = []

ADDRESS_NUMBER_PATTERN = [[['NUM'] for _ in range(i)] for i in range(1, 6)]

ADDRESS_NUMBER_PATTERN += [
  [['NUM'] for _ in range(i)] 
  + [['ZERO'] for _ in range(j)] 
  + [['NUM'] for _ in range(k)] 
  + [['ZERO'] for _ in range(l)] 
  + [['NUM'] for _ in range(m)]
  for i in range(1, 5) \
  for j in range(1, 4) \
  for k in range(0, 3) \
  for l in range(0, 2) \
  for m in range(0, 2)
]

ADDRESS_NUMBER_PATTERN = [_ for _ in ADDRESS_NUMBER_PATTERN if len(_) < 6]

def removeSpaces(transcript):
  return ''.join(transcript.split(' '))

ENTITY_DEFINITION = {
  'extraTokens': (ZERO, ),
  'patterns': ADDRESS_NUMBER_PATTERN,
  'extraCleaning': {
    'ZERO': text2int
  },
  'spacing': {
    'ZERO': '',
    'NUM': ''
  },
  'entityCleaning': removeSpaces
}
