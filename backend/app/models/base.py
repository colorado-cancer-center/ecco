"""
Base classes for models, originally derived from cancerinfocus.org ("cif")
but used elsewhere now, e.g. for the disparities index.
"""

from typing import Optional

from sqlmodel import Field, SQLModel

# ---------------------------------------------------------------------------
# -- base models that don't actually become tables
# ---------------------------------------------------------------------------

class BaseStatsModel(SQLModel):
    id: Optional[int] = Field(default=None, nullable=False, primary_key=True)

class MeasuresByCounty(BaseStatsModel):
    FIPS : str = Field(index=True)
    County : str = Field(index=True)
    State : str = Field(index=True, foreign_key="us_state.name")
    measure : str = Field(index=True)
    value : float = Field(nullable=True)

class MeasuresByTract(MeasuresByCounty):
    Tract : Optional[str] = Field(index=True, nullable=True)

# aggregate metadata for all measure-type models
from .cif import (
    STATS_MODELS as CIF_STATS_MODELS,
    MEASURE_DESCRIPTIONS as CIF_MEASURE_DESCRIPTIONS,
    CIF_FACTOR_DESCRIPTIONS
)
from .disparity_index import DISPARITY_INDEX_MODELS
from .scp import SCP_MODELS, SCP_MEASURE_DESCRIPTIONS, SCP_FACTOR_DESCRIPTIONS

STATS_MODELS = {
    "county": (
        CIF_STATS_MODELS["county"] +
        DISPARITY_INDEX_MODELS["county"] +
        SCP_MODELS["county"]
    ),
    "tract": (
        CIF_STATS_MODELS["tract"] + 
        DISPARITY_INDEX_MODELS["tract"] +
        SCP_MODELS["tract"]
    )
}

MEASURE_DESCRIPTIONS = {
    **CIF_MEASURE_DESCRIPTIONS,
    **SCP_MEASURE_DESCRIPTIONS
}

FACTOR_DESCRIPTIONS = {
    **CIF_FACTOR_DESCRIPTIONS,
    **SCP_FACTOR_DESCRIPTIONS,
}
