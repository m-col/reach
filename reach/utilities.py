"""
Utilities
=========

Miscellaneous utilities that do not fit into any main class.

"""


import functools


class lazy_property:
    """
    Method decorator that results in property functions being replaced by the
    result of their first call, so future calls do not recalculate the same
    values.
    """
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value


def enforce_suffix(string, suffix):
    """
    Append suffix to string if not present.
    """
    if not string.endswith(suffix):
        string = string + suffix

    return string
