#!/usr/bin/env python3


def formatting(entity):
    """
    >>> formatting('five k')
    'five k'
    >>> formatting('five k up')
    'five k'
    >>> formatting('five by five')
    'five'
    """

    entity = str(entity).split()
    stop_word_index = entity.index('by') if 'by' in entity else None
    stop_word_index = entity.index('up') if 'up' in entity and stop_word_index is None else stop_word_index

    return 'on ' + " ".join(_ for _ in (entity[:stop_word_index] if stop_word_index is not None else entity))

if __name__=="__main__":
    import doctest
    doctest.testmod(verbose=True)