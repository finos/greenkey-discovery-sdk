#!/usr/bin/env python
# coding: utf8
"""Example of a spaCy v2.0 pipeline component that sets entity annotations
based on list of single or multiple-word company names. Companies are
labelled as ORG and their spans are merged into one token. Additionally,
._.has_tech_org and ._.is_tech_org is set on the Doc/Span and Token
respectively.
* Custom pipeline components: https://spacy.io//usage/processing-pipelines#custom-components
Compatible with: spaCy v2.0.0+

# Fruit Interpreter
# colors and products that may be that color
# red - apple, tomato (fruit)
# green - tomato (vegetable)
# orange - carrot
# purple - carrot
# color may be unspecified (as it is for oranges)

"""
from __future__ import unicode_literals, print_function

import plac
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token


# Colors
class ColorRecognizer:
  """
  set entity annotations based on list of single or multi-word color words
  colors labeled COLOR and their spans merged into a single token
   ._.has_tech_org is set on Doc/Span
   ._.is_tech_org  set on Token
  """
  name = 'color_terms'  # component name shows up in pipeline

  def __init__(self, nlp, color_terms=tuple(), label='COLOR'):
    """
    Initialize pipeline component.
      - the shared NLP instance is used to:
            - initialize the matcher with the shared vocab
            - get the label ID
            - generate Doc objects as phrase match patterns
    """
    self.label = nlp.vocab.strings[label]    # get entity label ID

    # set up phrase mather - it can take Doc objects as patterns
    # so even if list of colors is long, it's very efficient
    patterns = [nlp(color) for color in color_terms]
    self.matcher = PhraseMatcher(nlp.vocab)
    self.matcher.add('COLOR_TERMS', None, *patterns)

    # register attribute on token; will override this based on matches, so just setting default value not a getter
    Token.set_extension('is_color_term', default=False)

    # register attribtues on Doc and Span via a getter that checks if one of the contained tokens is set to is_color=True
    Doc.set_extension('has_color_term', getter=self.has_color_term)
    Span.set_extension('has_color_term', getter=self.has_color_term)

  def __call__(self, doc):
      """
      Apply pipeline component on a Doc object and modify it
      if matches are found return the doc so it can be processed
      by the next component in the pipeline, if available
      """
      matches = self.matcher(doc)
      spans = []  # keep the spans for later so we can merge them afterwards

      for _, start, end in matches:
        # generate Span representing the entity and set label
        entity = Span(doc, start, end, label=self.label)
        spans.append(entity)
        for token in entity:
          token._.set('is_color_term', True)
        # Overwrite doc.ents and add entity - do not replace!
        doc.ents = list(doc.ents) + [entity]
      for span in spans:
        # iterate over all spans and merge into one token.
        # done after adding entities - otherwise cause mismatched indices
        span.merge()
      return doc        # don't forget to return doc

  def has_color_term(self, tokens):
      """
      Getter for Doc and Span attributes.
      Returns True if on eof the tokens is a color term
         Since the getter is only called when we access the attribute,
         we can refer to the Token's is_color_term attribtue here
         which is already set during the processing step
         """
      return any(t._.get('is_color_term') for t in tokens)
