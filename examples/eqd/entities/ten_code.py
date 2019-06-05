#!/usr/bin/env python3
"""
  Entity definition for a ten-code including some new primitives
  >>> TEN_CODE.get_lattice({"transcript": "i have not seen the suspect ten four"})
  >>> print(TEN_CODE.print_lattice())
  ============================================================================================
       start      stop                            entities                               words
  --------------------------------------------------------------------------------------------
         0.0       0.0                                None                                   i
         0.0       0.0                                None                                have
         0.0       0.0                                None                                 not
         0.0       0.0                                None                                seen
         0.0       0.0                                None                                 the
         0.0       0.0                                None                             suspect
         0.0       0.0                                 TEN                                 ten
         0.0       0.0                                 NUM                                four
  ============================================================================================
  >>> sorted(list(TEN_CODE.entity_dict.keys()))
  ['NUM', 'TEN']
  >>> TEN_CODE.get_matches()[0]
  ['10-4']
"""
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive

# Let's label ten as a special token
TEN = Primitive(label='TEN', tokens=['ten'], cleaning_function=lambda word: "10")

TEN_CODE = Entity({'patterns': "@TEN @NUM{1,3}", 'spacer': '-', "entities": TEN})

if __name__ == '__main__':
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
