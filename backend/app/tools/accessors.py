""""
Helper methods for interacting with dicts and other data
structures in Python
"""

def get_or_key(target, key):
    """
    Get a value from a target dict-like or return the key if it doesn't exist
    or is falsey.
    """
    return target.get(key, key) or key

def get_keys(d, *k):
    """
    Get the values corresponding to the given keys in the provided dict.

    This can be used in a destructuring assignment from a dict into variables,
    e.g. for a dict {'a': 1, 'b': 2, 'c': 3} you could extract the values of 'a'
    and 'b' with `a, b = dictget(d, 'a', 'b')`.

    >>> dictget({'a': 1, 'b': 2, 'c': 3}, 'a', 'b')
    (1, 2)
    """
    return [d[i] for i in k]
