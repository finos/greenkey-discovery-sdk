#!/usr/bin/env python3

"""
Validation function for upcoming year where it must be between 2017 and 2050
"""

from discovery.nlp.clean_text import text2int

def validation(entity):
  try:
    int_entity=text2int(entity)
    return int_entity > 17 and int_entity < 50
  except:
    return False