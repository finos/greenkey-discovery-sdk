#!/usr/bin/env python3
"""
  Entity definition for an address including some new primitives
  >>> sorted(list(ADDRESS.entity_dict.keys()))
  ['DIRECTION', 'NUM', 'NUM_ORD', 'STREET_NAME', 'STREET_TYPE']
  >>> ADDRESS.get_lattice({"transcript": "fifty five west monroe ave"})
  >>> print(ADDRESS.print_lattice())
  ============================================================================================
       start      stop                            entities                               words
  --------------------------------------------------------------------------------------------
         0.0       0.0                                 NUM                               fifty
         0.0       0.0                                 NUM                                five
         0.0       0.0                           DIRECTION                                west
         0.0       0.0                         STREET_NAME                              monroe
         0.0       0.0                         STREET_TYPE                                 ave
  ============================================================================================
  >>> results = ADDRESS.get_matches()
  >>> print(results[0])
  ['55 West Monroe Ave', '55 West Monroe', '5 West Monroe Ave', '5 West Monroe']
"""
from interpreters.primitive_entity import Primitive
from interpreters.entity import Entity

DIRECTION = Primitive(label='DIRECTION', tokens=('north', 'south', 'east', 'west'))
STREET_NAME = Primitive(label='STREET_NAME', file='chicago_street_names.txt')
STREET_TYPE = Primitive(label='STREET_TYPE', file='street_types.txt')
ADDRESS = Entity(
  patterns="@NUM{1,6} @DIRECTION? (@STREET_NAME|@NUM_ORD) STREET_TYPE?", entities=[DIRECTION, STREET_NAME, STREET_TYPE]
)

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
