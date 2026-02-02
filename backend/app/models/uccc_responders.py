"""
Model derived from UCCC survey responders by zip code, but we aggregate in this
model at the county level and show the number of responders in each county
as the measure's value. Note that urban/rural is established at the county
level; despite being included for each zip code, all the zip codes have
the same urban/rural value as their parent county.

See https://github.com/colorado-cancer-center/ecco/issues/150 for the source
data and more context.
"""

from sqlmodel import Field

from .base import MeasureUnit, MeasuresByCounty

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class UCCCRespondersCounty(MeasuresByCounty, table=True):
    class Config:
        label = "UCCC Survey Responders"

    # differentiates between urban vs rural responders
    urbanicity: str = Field(nullable=True, index=True)

    @classmethod
    def get_factors(cls):
        return (cls.urbanicity,)

# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

UCCC_RESPONDERS_MODELS = {
    "county": [
        UCCCRespondersCounty
    ],
}

UCCC_RESPONDERS_MEASURE_DESCRIPTIONS = {
    "ucccresponders": {
        "responses": {
            "label": "Total Responses",
            "unit": MeasureUnit.COUNT,
        },
    }
}

UCCC_RESPONDERS_FACTOR_DESCRIPTIONS = {
    "ucccresponders": {
        "urbanicity": {
            "label": "Urbanicity",
            "default": "All",
            "values": {"All": "All", "Urban": "Urban", "Rural": "Rural"},
        },
    },
}
