#!/usr/bin/env python3
"""
  Entity definition for a decimal including some new primitives
  >>> GRAPH.get_lattice({"transcript": "pull up a g spread on microsoft"})
  >>> GRAPH.get_matches()[0]
  ['G-SPREAD']
"""

from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

PREFIX = Primitive({'label': 'PREFIX', 'tokens': ('t', 'g', 'i', 'z')})
SPREAD = Primitive({'label': 'SPREAD', 'tokens': ['spread'], 'cleaning_function': lambda word: word.upper()})

GRAPH = Entity({'patterns': "@PREFIX @SPREAD", 'spacer': '-'}, entities=[PREFIX, SPREAD])
if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
