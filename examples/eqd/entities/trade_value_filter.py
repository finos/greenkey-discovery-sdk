#!/usr/bin/env python3
"""
  Entity definition for a period of time
  >>> TRADE_VALUE.get_lattice({"transcript": "it's over eleven"})
  >>> print(TRADE_VALUE.print_lattice())
  ============================================================================================
       start      stop                            entities                               words
  --------------------------------------------------------------------------------------------
         0.0       0.0                                None                                it's
         0.0       0.0                           DIRECTION                                over
         0.0       0.0                                 NUM                              eleven
  ============================================================================================
  >>> TRADE_VALUE.get_matches()[0]
  ['Over 11']
"""
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

DIRECTION = Primitive({'label': 'DIRECTION', 'tokens': ('above', 'over', 'exceeding', 'below', 'under')})

TRADE_VALUE = Entity({'patterns': "@DIRECTION @NUM{1,9}"}, entities=[DIRECTION])
if __name__ == '__main__':
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
