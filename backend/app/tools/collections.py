"""
Utilities for producing things that look like collections,
but generate the values on the fly.
"""

from models.base import MeasureUnit

class MeasureMapper(dict):
    """
    A dict-like that, given a key, produces a result like { label: <key>, unit:
    <default_unit> }

    This is useful for many of our stats models where the key for a measure and
    its label are the same, and the unit is shared across lots of different
    measures.
    """
    
    def __init__(self, default_unit:MeasureUnit):
        self.default_unit = default_unit

    def __getitem__(self, key):
        return {
            "label": key,
            "unit": self.default_unit,
        }

    def __setitem__(self, *args, **kwargs) -> None:
        raise NotImplementedError("MeasureMapper is read-only")
