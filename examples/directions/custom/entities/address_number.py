''' this contians the entity definition for an address number '''
# Each interpreter needs a list of patterns to look for

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

def remove_spaces(transcript):
  return ''.join(transcript.split(' '))
  
def clean_zero(wordList, spacer):
  return '0'

ENTITY_DEFINITION = {
  'extraTokens': (ZERO, ),
  'patterns': ADDRESS_NUMBER_PATTERN,
  'extraCleaning': {
    'ZERO': clean_zero
  },
  'spacing': {
    'ZERO': '',
    'NUM': ''
  },
  'entityCleaning': remove_spaces
}
