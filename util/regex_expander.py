#!/usr/bin/env python3
"""
Module of helper functions for dealing with patterns in entity regex.
"""

import re
from itertools import chain

import exrex


def make_clean_input(pattern):
    """
    Enforces that entities or words have parentheses around them and have trailing spaces
    >>> make_clean_input("@num{3}")
    '(@(num ) ){3}'
    >>> make_clean_input("num{3}")
    '(num ){3}'

    Entities can sometimes have underscores
    >>> make_clean_input("@NUM_PLURAL{3}")
    '(@(NUM_PLURAL ) ){3}'

    Entities or words should have at least one character
    >>> make_clean_input("a{10}")
    '(a ){10}'
    """
    entity_pattern = re.compile(r"(@[a-zA-Z\_][\w]*)")
    pattern = re.sub(
        entity_pattern, lambda match: "({} )".format(match.group()), pattern
    )

    word_pattern = re.compile(r"([a-zA-Z\_][\w]*)")
    pattern = re.sub(word_pattern, lambda match: "({} )".format(match.group()), pattern)
    return pattern


def strip_extra_spaces(input_string):
    """
    Removes extra spaces from input string
    >>> strip_extra_spaces("I have no  cats")
    'I have no cats'
    """
    while "  " in input_string:
        input_string = input_string.replace("  ", " ")
    return input_string


def expand_this(pattern):
    """
    Cleans then expands any and all patterns
    >>> expand_this("@num{1,2}")
    [['@num'], ['@num', '@num']]
    >>> expand_this("spam{3}")
    [['spam', 'spam', 'spam']]
    >>> expand_this("(a|f) b c")
    [['a', 'b', 'c'], ['f', 'b', 'c']]
    >>> expand_this("a{10}")
    [['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']]
    >>> expand_this("@banana_2{1,2}")
    [['@banana_2'], ['@banana_2', '@banana_2']]
    """
    pattern = make_clean_input(pattern)
    patterns = [strip_extra_spaces(_).split() for _ in exrex.generate(pattern)]
    return patterns


def expand_these(patterns):
    """
    Cleans then expands any and all patterns
    >>> expand_these("@num{1,2}")
    [['@num'], ['@num', '@num']]
    >>> expand_these(["Lovely spam{3}", "wonderful spam{4}"])
    [['Lovely', 'spam', 'spam', 'spam'], ['wonderful', 'spam', 'spam', 'spam', 'spam']]

    Now for things without regex - make sure we don't do anything to patterns like these
    >>> expand_these([[['a', 'f'], 'b', 'c'], ['b', 'c', 'f']])
    [[['a', 'f'], 'b', 'c'], ['b', 'c', 'f']]
    >>> expand_these(['a test'.split()])
    [['a', 'test']]
    >>> expand_these([["@num", "@letter"]])
    [['@num', '@letter']]

    This handles strings by themselves too now
    >>> expand_these('a test')
    [['a', 'test']]

    Handle repeated patterns
    >>> expand_these(["@num{1,2}", "@letter? @num{1,2}"])
    [['@num'], ['@num', '@num'], ['@letter', '@num'], ['@letter', '@num', '@num']]
    """
    if isinstance(patterns, str):
        output = expand_this(patterns)
    else:
        output = list(
            chain.from_iterable(
                [expand_this(_) if isinstance(_, str) else [_] for _ in patterns]
            )
        )

    unique_patterns = []
    for pattern in output:
        if pattern not in unique_patterns:
            unique_patterns.append(pattern)
    return unique_patterns


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=False, verbose=True)
