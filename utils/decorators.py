import types
from functools import partial

supported_attributes = ["__abs__", "__add__", "__and__", "__ceil__", "__copy__"
                        "__divmod__", "__eq__", "__floor__", "__floordiv__",
                        "__ge__", "__gt__", "__invert__", "__le__", "__lshift__",
                        "__lt__", "__mod__", "__mul__", "__ne__", "__neg__", "__or__",
                        "__pos__", "__pow__", "__radd__", "__rand__", "__rdivmod__",
                        "__rfloordiv__", "__rlshift__", "__rmod__", "__rmul__",
                        "__ror__", "__round__", "__rpow__", "__rrshift__", "__rshift__", "__rsub__",
                        "__rtruediv__", "__rxor__", "__sub__", "__truediv__", "__trunc__", "__xor__"]


def _make_encapsulating_function(original, base, method):
    # This needs to be a separate function, otherwise all the encapsulated methods will reference to the
    # last method changed (for complex, this is '__truediv__')
    base_method = getattr(base, method)

    def encapsulated(*args, **kwargs):
        result = base_method(*args, **kwargs)
        if isinstance(result, base):
            return original(result)
        else:
            return result

    return encapsulated


def encapsulate_parent(additional_methods=None):
    """
    This decorator encapsulates all magic methods (like ``__add__`` and ``__eq__``)
    to return the same result, but then transformed to its parent class. This makes
    it easy to add wrapper classes for built-in types like int and complex.
    :param additional_methods: optional additional methods to encapsulate
    :return: the encapsulated class
    """
    if additional_methods is None:
        additional_methods = []

    def inner(original):
        base = original.__bases__[0]
        for method in filter(lambda x: x in dir(base), supported_attributes + additional_methods):
            setattr(original, method, _make_encapsulating_function(original, base, method))
        return original

    return inner
