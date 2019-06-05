#!/usr/bin/env python3
"""
  Entity definition for a decimal including some new primitives
  >>> LICENSE_PLATE.get_lattice({"transcript": "there's a red car alpha bravo q one two seven"})
  >>> LICENSE_PLATE.get_matches()[0]
  ['ABQ127']
"""

from interpreters.entity import Entity

LICENSE_PLATE = Entity(
  {
    'patterns': ["(@LETTER|@NUM){6,8}"]
  },
  formatting=lambda text: text.replace(" ", ""),
)

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
