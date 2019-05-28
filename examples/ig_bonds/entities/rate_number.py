#!/usr/bin/env python3
"""
  Entity definition for a rate including some new primitives
  >>> RATE.get_lattice({"transcript": "one spot two"})
  >>> RATE.get_matches()[0]
  ['1.2']
"""
from definitions.entities import NUM
from definitions.entities.financial_decimal import DECIMAL
from copy import deepcopy


def valid_rate(rate):
  """
    No bonds return over 11 % interest
  """
  return float(rate) < 11


RATE = deepcopy(DECIMAL)
RATE.patterns = [[NUM] + pattern for pattern in DECIMAL.patterns]

RATE.validation = valid_rate

if __name__ == '__main__':
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)
