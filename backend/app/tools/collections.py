"""
Utilities for producing things that look like collections,
but generate the values on the fly.
"""

from collections.abc import Mapping

from models.base import MeasureUnit

class MeasureMapper(Mapping):
    """
    A dict-like that, given a key, produces a result like { label: <key>, unit:
    <default_unit> }

    This is useful for many of our stats models where the key for a measure and
    its label are the same, and the unit is shared across lots of different
    measures.

    Also supports a dictionary of extras, which can be used to add information
    to each request for a key.
    """

    def __init__(self, default_unit: MeasureUnit, extras: dict=None):
        self.default_unit = default_unit
        self.extras = extras or {}

    def __getitem__(self, key):
        return {**{"label": key, "unit": self.default_unit}, **self.extras}
    
    def get(self, key, default=None):
        return {**{"label": key, "unit": self.default_unit}, **self.extras}
    
    def __len__(self):
        """
        Returns 0, since the object has virtual keys and thus
        there's nothing to count.
        """
        return 0

    def __iter__(self):
        """
        Returns an empty iterator, since the object has virtual keys and thus
        there's nothing to iterate over.
        """
        return iter([])
    
    def __repr__(self):
        return f"MeasureMapper(default_unit={self.default_unit})"
    
    def __str__(self):
        return repr(self)
