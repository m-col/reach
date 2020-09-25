"""
Utilities
=========

Miscellaneous utilities.
"""

import functools


class cache:  # pylint: disable=invalid-name,too-few-public-methods
    """
    Property decorator to cache the return value of its first call.
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
