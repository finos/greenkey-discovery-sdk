#!/usr/bin/env python3
"""
  Entity definition for a decimal including some new primitives
  >>> FRACTION.get_lattice({"transcript": "one half"})
  >>> FRACTION.get_matches()[0]
  ['.5']
"""
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

from nlp.clean_text import clean_fractions

ONE_THROUGH_SEVEN = Primitive(
  {
    'label': 'ONE_THROUGH_SEVEN',
    'tokens': ('a', 'an', 'one', 'two', 'three', 'four', 'five', 'six', 'seven')
  }
)

DENOMINATOR = Primitive({'label': 'DENOMINATOR', 'tokens': ('quarter', 'fourth', 'half', 'eighth', 'eight')})

FRACTION_PATTERNS = [[[ONE_THROUGH_SEVEN], [DENOMINATOR]]]

FRACTION = Entity(
  patterns=FRACTION_PATTERNS, _clean_transcript=lambda word_list, entity_list: clean_fractions(" ".join(word_list))
)

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)