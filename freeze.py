#!/usr/bin/env python3
"""
Freezes objects into immutable objects so they can hash
Also contains wrapper for freezing arguments to lru_cache and unfreeze routine
"""
import collections
import functools

from immutables import Map


def freeze_map(obj):
    """
    freezes components of all mappables
    """
    return Map({key: freeze(value) for key, value in obj.items()})


def freeze_iter(obj):
    """
    freezes components of all iterables
    """
    return (frozenset if isinstance(obj, set) else tuple)(freeze(i) for i in obj)


def raise_freezing_error(obj):
    """
    Custom error message with type of object
    """
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
        pass
    elif isinstance(obj, collections.abc.Mapping):
        obj = freeze_map(obj)
    elif isinstance(obj, collections.abc.Iterable):
        obj = freeze_iter(obj)
    else:
        raise_freezing_error(obj)
    return obj


def unfreeze_map(obj):
    """
    Unfreezes all elements of mappables
    """
    return {key: unfreeze(value) for key, value in obj.items()}


def unfreeze_iter(obj):
    """
    Unfreezes all elements of iterables
    """
    return list(unfreeze(i) for i in obj)


def unfreeze_set(obj):
    """
    Unfreezes all elements of frozensets
    """
    return set(unfreeze(i) for i in obj)


def unfreeze(obj):
    """Convert all map objects to dicts.

    >>> map_object = Map({
    ...   "key": Map({"nested_key": "nested_value"})
    ... })
    >>> unfreeze(map_object)
    {'key': {'nested_key': 'nested_value'}}
    """
    if isinstance(obj, (str, int, float, bool)):
        pass
    elif isinstance(obj, frozenset):
        obj = unfreeze_set(obj)
    elif isinstance(obj, collections.abc.Mapping):
        obj = unfreeze_map(obj)
    elif isinstance(obj, collections.abc.Iterable):
        obj = unfreeze_iter(obj)
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
