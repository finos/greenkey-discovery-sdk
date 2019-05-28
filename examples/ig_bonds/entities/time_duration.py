#!/usr/bin/env python3
"""
  Entity definition for a period of time
  >>> TIME_DURATION.get_lattice({"transcript": "i have not seen the suspect in four months"})
  >>> TIME_DURATION.get_matches()[0]
  ['4 months']
"""
from definitions.entities import NUM
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

SINGLE_UNITS = ('hour', 'day', 'week', 'month', 'year')
PLURAL_UNITS = tuple([unit + 's' for unit in SINGLE_UNITS])
TIME_UNIT = Primitive(
  {
    'label': 'TIME_UNIT',
    'tokens': (SINGLE_UNITS + PLURAL_UNITS),
    'cleaning_function': lambda word: word
  }
)

SPECIAL_TIME_UNIT = Primitive({'label': 'SPECIAL_TIME_UNIT', 'tokens': ('today', 'yesterday')})

TIME_DURATION_NUMBER = []
for i in range(1, 4):
  range_pattern = [[NUM] for _ in range(i)]
  TIME_DURATION_NUMBER.append(range_pattern)

TIME_DURATION_PATTERNS = [[[SPECIAL_TIME_UNIT]]]

for number in TIME_DURATION_NUMBER:
  pattern = number + [[TIME_UNIT]]
  TIME_DURATION_PATTERNS.append(pattern)

TIME_DURATION = Entity({'patterns': TIME_DURATION_PATTERNS})

if __name__ == '__main__':
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
