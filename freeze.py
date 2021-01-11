#!/usr/bin/env python3

import collections
import functools

from immutables import Map


def freeze_map(obj):
    return Map({key: freeze(value) for key, value in obj.items()})


def freeze_iter(obj):
    return (frozenset if isinstance(obj, set) else tuple)(freeze(i) for i in obj)


def raise_freezing_error(obj):
    msg = "Unsupported type: %r" % type(obj).__name__
    raise TypeError(msg)


def freeze(obj):
    """Convert data structure into an immutable data structure.

    >>> list_test = [1, 2, 3]
    >>> freeze(list_test)
    (1, 2, 3)
    >>> set_test = {1, 2, 3}
    >>> freeze(set_test)
    frozenset({1, 2, 3})
    """

    if isinstance(obj, collections.abc.Hashable):
        obj = obj
    elif isinstance(obj, collections.abc.Mapping):
        obj = freeze_map(obj)
    elif isinstance(obj, collections.abc.Iterable):
        obj = freeze_iter(obj)
    else:
        raise_freezing_error(obj)
    return obj


def freezeargs(func):
    """
    Transform all mutable objects into immutables using freeze
    For the sake of lru_cache
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple(freeze(arg) for arg in args)
        kwargs = {k: freeze(v) for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped
