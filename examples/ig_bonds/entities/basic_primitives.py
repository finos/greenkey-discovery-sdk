#!/usr/bin/env python3
"""
  This is a list of common primitives with simple definitions and some duck-typed cleaning functions
  See clean_text.py for doctests for cleaning functions
"""

# local imports
from nlp.constants import constants
from nlp.clean_text import format_ordinal, alpha_to_A, text2int
from interpreters.primitive_entity import Primitive

# instantiations of the Primitive class take us from default tokens to primitive entities
TIME_MONTH = Primitive(label="TIME_MONTH", tokens=constants['months'])
TIME_DAY = Primitive(label="TIME_DAY", tokens=constants['days'])
TIME_WEEK = Primitive(label="TIME_WEEK", tokens=constants['weeks'])

# LETTER = Primitive(label="LETTER", tokens=constants['letters'], formatting=alpha_to_A)

# Numbers are frequently special


class NumClass(Primitive):
  label = "NUM"
  tokens = constants['numbers']

  def cleaning(self, word_list, spacer=None):
    if spacer is None:
      spacer = self.spacer
    return text2int(word_list, spacer) if isinstance(word_list, list) else text2int(word_list.split(), spacer)


NUM = NumClass()


class OrdinalClass(Primitive):
  label = "NUM_ORD"
  tokens = constants['ordinals']

  def cleaning(self, word_list, spacer=None):
    if spacer is None:
      spacer = self.spacer
    return format_ordinal(word_list, spacer)


class Letter(Primitive):
  label = "LETTER"
  tokens = constants['letters']

  def cleaning(self, word_list, spacer=None):
    if spacer is None:
      spacer = self.spacer
    return alpha_to_A(word_list, spacer)


LETTER = Letter()

NUM_ORD = OrdinalClass()

NUM_PLURAL = NumClass(label="NUM_PLURAL", tokens=constants['plural_numbers'], formatting=text2int)

default_entity_dict = {
  "NUM": NUM,
  "TIME_MONTH": TIME_MONTH,
  "TIME_DAY": TIME_DAY,
  "TIME_WEEK": TIME_WEEK,
  "LETTER": LETTER,
  "NUM_ORD": NUM_ORD,
  "NUM_PLURAL": NUM_PLURAL
}
