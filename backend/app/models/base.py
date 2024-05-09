"""
Base classes for models, originally derived from cancerinfocus.org ("cif")
but used elsewhere now, e.g. for the disparities index.
"""

from enum import Enum
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

class CancerStatsByCounty(BaseStatsModel):
    # NOTE: the 'measure' and 'value' columns are named 'Site' and 'AAR' in the
    # original schema, but we rename them here so they can be treated in
    # the same way as the other stats.
    
    # this base model is shared between the CIF and SCP models and will likely
    # be shared with any other cancer stats models we encounter. it won't
    # contain any stratifying factors; child models should include those on
    # their own.

    FIPS : str = Field(index=True)
    County : str = Field(index=True)
    State : str = Field(index=True, foreign_key="us_state.name")

    # the type of cancer
    Site : str = Field(index=True)
    # average annual rate
    AAR : float
    # average annual count (typically age-adjusted per 100k)
    AAC : float

    @classmethod
    def get_factors(cls):
        """
        Returns a set of factors to include in, e.g., downloaded CSVs.

        This is a placeholder method that should be overridden by child models.
        """
        return ()

class MeasuresByTract(MeasuresByCounty):
    Tract: Optional[str] = Field(index=True, nullable=True)


# ---------------------------------------------------------------------------
# -- metadata about the models
# ---------------------------------------------------------------------------


class MeasureUnit(Enum):
    """
    The unit of measurement for a given measure, exposed as the 'unit' field in the API
    endpoint's fips-values response.

    The 'ratio' unit is a bit complicated; see https://cancerinfocus.org/datasources/, specifically the
    indices of segregation for examples.
    """

    PERCENT = "percent" # a percentage; the datasets we use encode these as floats between 0 and 1, inclusive
    COUNT = "count" # raw count, represented as an integer, e.g. number of cases
    RATE = "rate" # rate of occurrence, represented as a float and typically normalized by population
    DOLLAR_AMOUNT = "dollar_amount" # raw dollar amount, e.g. income
    RANK = "rank" # a position in a ranking
    ORDINAL = "ordinal" # a discrete value that can be ordered, e.g. "rising" (1), "falling" (2), "stable" (3)
    CATEGORICAL = "categorical" # a discrete value that *can't* be ordered, e.g. "white", "black", "hispanic"
    RATIO = "ratio" # range from -1 to +1, where -1 is "least affected" and +1 is "most affected". 


from .cif import (
    STATS_MODELS as CIF_STATS_MODELS,
    CIF_CANCER_MODELS,
    CIF_MEASURE_DESCRIPTIONS,
    CIF_FACTOR_DESCRIPTIONS
)
from .disparity_index import (
    DISPARITY_INDEX_MODELS,
    DISPARITY_INDEX_MEASURE_DESCRIPTIONS,
)
from .scp import (
    SCP_MODELS,
    SCP_MEASURE_DESCRIPTIONS,
    SCP_FACTOR_DESCRIPTIONS,
    SCP_CANCER_MODELS,
)

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

# to match the input schema, cancer models have columns named "Site" and "AAR"
# instead of "measure" and "value". they also include an "AAC" field that's passed
# along to the frontend and displayed just for cancer models.
#  to keep track of this special treatment, we enumerate the cancer models
# separately from the other stats models.
CANCER_MODELS = set.union(SCP_CANCER_MODELS, CIF_CANCER_MODELS)

MEASURE_DESCRIPTIONS = {
    **CIF_MEASURE_DESCRIPTIONS,
    **SCP_MEASURE_DESCRIPTIONS,
    **DISPARITY_INDEX_MEASURE_DESCRIPTIONS
}

FACTOR_DESCRIPTIONS = {
    **CIF_FACTOR_DESCRIPTIONS,
    **SCP_FACTOR_DESCRIPTIONS,
}
