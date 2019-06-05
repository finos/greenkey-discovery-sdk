#!/usr/bin/env python3
"""
  Entity definition for a decimal including some new primitives
  >>> DECIMAL.get_lattice({"transcript": "one spot two"})
  >>> DECIMAL.get_matches()[0]
  ['.2', '2', '1']
"""
from definitions.entities import NUM
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

SPOT = Primitive({'label': 'SPOT', 'tokens': ('spot', 'point', 'dot')}, cleaning_function=lambda _: '.')

# may or may not give spot
DECIMAL = Entity(
  label='DECIMAL',
  spacer='',
  patterns=[
    [[NUM]],
    [[NUM], [NUM]],
    [[NUM], [NUM], [NUM]],
    [[SPOT], [NUM]],
    [[SPOT], [NUM], [NUM]],
    [[SPOT], [NUM], [NUM], [NUM]],
    [[SPOT], [NUM], [NUM], [NUM], [NUM]],
  ]
)
if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)