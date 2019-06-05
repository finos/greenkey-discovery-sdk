#!/usr/bin/env python3
"""
  Entity definition for a simple sentence
  >>> BASIC_SENTENCE.get_lattice({"transcript": "he ate my pizza and he ate the whole thing"})
  >>> results = BASIC_SENTENCE.get_matches()
  >>> print(results[0])
  ['He Ate The Whole Thing', 'He Ate My Pizza']
"""

from interpreters.entity import Entity

# This may eventually need tidying up for ontological tags. Logic to be fixed up is in nlp/recognizer.py
NOUN = ["PRP", "WP", "NN", "NNS", "NNPS", "NNPS"]
VERB = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
MODIFIER = ["JJ", "JJR", "JJS", "PRP$", "PDT", "DT"]
ADVERB = ["RB", "RBR", "RBS"]
PREPOSITION = ["IN"]

SENTENCE_PATTERNS = []
# he ate pizza
SENTENCE_PATTERNS.append([NOUN, VERB, NOUN])
# he ate good pizza
SENTENCE_PATTERNS.append([NOUN, VERB, MODIFIER, NOUN])
# he ate his good pizza
SENTENCE_PATTERNS.append([NOUN, VERB, MODIFIER, MODIFIER, NOUN])
# he ate my very good pizza
SENTENCE_PATTERNS.append([NOUN, VERB, MODIFIER, ADVERB, MODIFIER, NOUN])

BASIC_SENTENCE = Entity(patterns=SENTENCE_PATTERNS, ontological_tags=True)

if __name__ == "__main__":
  import doctest
  doctest.testmod(raise_on_error=False, verbose=True)