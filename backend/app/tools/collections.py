"""
Utilities for producing things that look like collections,
but generate the values on the fly.
"""

from collections.abc import Mapping
from typing import ItemsView

from sqlmodel import select

from db import get_sync_session
from models.base import BaseStatsModel, MeasureUnit

class MeasureMapper(Mapping):
    """
    A dict-like that, given a key, produces a result like { label: <key>, unit:
    <default_unit> }

    This is useful for many of our stats models where the key for a measure and
    its label are the same, and the unit is shared across lots of different
    measures.

    Also supports a dictionary of extras, which can be used to add information
    to each request for a key.

    If 'model' is provided, issues queries against the model for the
    measures that it contains. Uses 'measure_column' as the column name for
    the measure in the model (for regulare measures, this is 'measure', but
    for cancer models, it's 'Site').
    """

    def __init__(self, default_unit: MeasureUnit, extras: dict=None, model: BaseStatsModel = None, measure_column: str = "measure"):
        self.default_unit = default_unit
        self.extras = extras or {}
        self.model = model
        self.measure_column = measure_column
        # cache for unique values of the measure column
        self._model_measures = None

    def _get_measures(self):
        if not self.model:
            return []
        
        if self._model_measures is None:
            # query for unique values of the measure column
            with get_sync_session() as session:
                query = select(getattr(self.model, self.measure_column)).distinct()
                result = session.execute(query)
                self._model_measures = result.scalars().all()

        return self._model_measures


    def __getitem__(self, key):
        return {**{"label": key, "unit": self.default_unit}, **self.extras}
    
    def get(self, key, default=None):
        return {**{"label": key, "unit": self.default_unit}, **self.extras}
    
    def __len__(self):
        """
        Returns 0, since the object has virtual keys and thus
        there's nothing to count.
        """

        return len(self._get_measures())

    def __iter__(self):
        """
        If a model was provided, attempts create an iterator over its measures.
        If not, returns an empty iterator, since the object has virtual keys and
        thus there's nothing to iterate over.
        """
        return iter([
            k for k in self._get_measures()
        ])
    
    def items(self) -> ItemsView:
        return iter([
            (k, self.get(k)) for k in self._get_measures()
        ])
    
    def __repr__(self):
        return f"MeasureMapper(default_unit={self.default_unit})"
    
    def __str__(self):
        return repr(self)
