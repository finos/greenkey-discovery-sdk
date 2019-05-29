#!/usr/bin/env python3


def formatting(entity):
  """
    >>> formatting('five k')
    'five k'
    >>> formatting('five k up')
    'five k'
    >>> formatting('five by six')
    'six'
    """

  entity = str(entity).split()

  stop_word_index = entity.index('up') if 'up' in entity else None
  start_word_index = entity.index('by') if 'by' in entity else None

  # trim off end
  entity = " ".join(_ for _ in (entity[:stop_word_index] if stop_word_index is not None else entity)).split()

  # trim off beginning
  entity = " ".join(_ for _ in (entity[start_word_index + 1:] if start_word_index is not None else entity))

  return 'on ' + entity


if __name__ == "__main__":
  import doctest
  doctest.testmod(verbose=True)