#!/usr/bin/env python3
"""
  Entity definition for a decimal including some new primitives
  >>> NUMBER_OF_TRADES.get_lattice({"transcript": "pull up my last ten trades over one million in microsoft thirty six"})
  >>> NUMBER_OF_TRADES.get_matches()[0]
  ['Last 10 Trades']
"""
from interpreters.entity import Entity
from interpreters.primitive_entity import Primitive
from definitions.entities.basic_primitives import NUM
from copy import deepcopy

# Set space between matching characters
NUM = deepcopy(NUM)
NUM.spacer = ''

PREVIOUS = Primitive({
  'label': 'PREVIOUS',
  'tokens': ('last', 'previous', 'prior'),
})

TRADES = Primitive({
  'label': 'TRADES',
  'tokens': ('trades', 'transactions', 'sales', 'trade', 'transaction', 'sale'),
})

NUMBER_OF_TRADES = Entity({'patterns': "@PREVIOUS @NUM{0,3} @TRADES", 'entities': [PREVIOUS, TRADES, NUM]})

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)