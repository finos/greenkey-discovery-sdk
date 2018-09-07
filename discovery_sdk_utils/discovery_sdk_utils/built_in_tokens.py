#!/usr/bin/python

ONTOLOGICAL_TAGS = (
    'IN',
    'VB',
    'NNPS',
    'VBG',
    'RB',
    'NN',
    'VBD',
    'RBS',
    'RBR',
    'PDT',
    'JJS',
    'VBN',
    'JJR',
    'VBP',
    'PRP',
    'JJ',
    'WP',
    'VBZ',
    'DT',
    'PRP$',
    'NNS',
)

DISCOVERY_TOKENS = (
    "NUM",
    "LETTER",
    "NUM_ORD",
    "NUM_PLURAL",
    "TIME_MONTH",
    "TIME_DAY",
    "TIME_WEEK",
)

BUILT_IN_TOKENS = ONTOLOGICAL_TAGS + DISCOVERY_TOKENS
