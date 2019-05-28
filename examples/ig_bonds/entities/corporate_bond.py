#!/usr/bin/env python3
"""
  Entity definition for an address including some new primitives
  >>> CORPORATE_BOND.get_lattice({"transcript": "I want to buy a yard of matter horn twenty fours"})
  >>> CORPORATE_BOND.get_matches()[0]
  ['Matterhorn 24', 'Matterhorn 20', 'Matterhorn']
  >>> CORPORATE_BOND.get_lattice({"transcript": "soft bank twenty two par and one eighth"})
  >>> CORPORATE_BOND.get_matches()[0]
  ['Softbk 22', 'Softbk 20', 'Softbk']
"""

from interpreters.primitive_entity import Primitive
from interpreters.entity import Entity

ticker_list = (
  'upcb', 'softbk', 'cmacg', 'tnetbb', 'fedmob', 'intnet', 'gament', 'sunshm', 'sek', 'smurf', 'caffil', 'alta', 'cck',
  'matterhorn', 'c', 'ttmtin', 'netflix', 'vmed', 'oi', 'unity', 'uktb', 'bacr', 'argos', 'levi', 'car', 'ijss',
  'crunav', 'ctlt', 'rx', 'altees', 'ball', 'daigr', 'sfr', 'cbsbkf', 'negrp', 'faurecia', 'euroca', 'ziggo', 'windim',
  'adrbid', 'adient'
)
collapsible_patterns = [
  ("o i", "oi"), ("b l l", "ball"),
  ("c c k", "cck"), ("o e f p", "eofp"), ("c m a c g", "cmacg"), ("adr bid", "adrbid"), ("a d r bid", "adrbid"),
  ("soft bank", "SOFTBK"), ("telenet", "TNETBB"), ("t net b b", "TNETBB"), ("t net broadband", "TNETBB"),
  ("u p c b", "UPCB"), ("v med", "VMED"), ("win dim", "WINDIM"), ("northeastern group", "NEGRP"),
  ("northeastern", "NEGRP"), ("tata motors", "TTMTIN"), ("tata", "TTMTIN"), ("i j s s", "IJSS"), ("r x", "RX"),
  ("federal mobiles", "fedmob"), ("matter horn", "matterhorn"), ("caisse francaise de fin", "caffil"),
  ("central bank of savings", "cbsbkf"), ("central bank", "cbsbkf"), ("central", "cbsbkf"),
  ("caja rural de navarra", "crunav"), ("caja rural", "crunav"), ("sunshine", "sunshm"), ("catalent", "ctlt"),
  ("levi strauss", "levi"), ("levi straus", "levi"), ("europe car", "euroca"), ("euro car", "euroca"),
  ("gamenet", "gament"), ("game net", "gament"), ("barclays", "bacr"), ("barclay", "bacr"), ("bar clays", "bacr"),
  ("bar clay", "bacr"), ("daimler", "daigr"), ("svensk", "sek"), ("ing", "intnet"), ("citi group", "c"), ("citi", "c"),
  ("united kingdom treasury bill", "uktb"), ("u k treasury bill", "uktb"), ("uk treasury bill", "uktb"),
  ("u k t bill", "uktb"), ("uk t bill", "uktb"), ("ukt bill", "uktb"), ("alberta", "alta")
]

TICKER = Primitive(label='TICKER', tokens=ticker_list, collapsible_patterns=collapsible_patterns)

CORPORATE_BOND = Entity(patterns="@TICKER (NUM|NUM_PLURAL){,2}", entities=TICKER)

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)