"""Memoization decorator implementation."""

from functools import wraps
from typing import Any, Callable, Hashable


def _make_hashable(value: Any) -> Hashable:
    """Convert nested mutable containers into hashable equivalents."""
    if isinstance(value, dict):
        return (
            dict,
            frozenset(
                (
                    _make_hashable(key),
                    _make_hashable(item),
                )
                for key, item in value.items()
            ),
        )

    if isinstance(value, list):
        return (
            list,
            tuple(_make_hashable(item) for item in value),
        )

    if isinstance(value, tuple):
        return (
            tuple,
            tuple(_make_hashable(item) for item in value),
        )

    if isinstance(value, set):
        return (
            set,
            frozenset(_make_hashable(item) for item in value),
        )

    return value


def memoize(func: Callable) -> Callable:
    """Cache and return function results for previously used arguments."""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (
            _make_hashable(args),
            _make_hashable(kwargs),
        )

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrapper
