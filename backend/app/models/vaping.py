"""
Model derived from youth vaping data for CO health regions, collections of
counties for which specific data is tracked.

More about health regions can be found here:
https://www.arcgis.com/home/item.html?id=75e32548d3b24169adb942ecb7424937

See https://github.com/colorado-cancer-center/ecco/issues/105 for details about
this model and its inclusion in ECCO.
"""

from sqlmodel import Field

from .base import MeasureUnit, MeasuresByHealthRegion

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class VapingHealthRegion(MeasuresByHealthRegion, table=True):
    class Config:
        label = "Youth Vaping"

    # pulled out for use as factors
    sex: str = Field(nullable=True, index=True)
    race: str = Field(nullable=True, index=True)
    age: str = Field(nullable=True, index=True)

    @classmethod
    def get_factors(cls):
        return (cls.sex, cls.race, cls.age)


# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

VAPING_MODELS = {
    "healthregion": [
        VapingHealthRegion
    ]
}

VAPING_MEASURE_DESCRIPTIONS = {
    "vaping": {
        "Youth Vaping Rate": {
            "label": "Youth Vaping Rate",
            "unit": MeasureUnit.RATE,
        }
    }
}

# for now, deaths and incidence share the same data
VAPING_FACTOR_DESCRIPTIONS = {
    "vaping": {
        "sex": {
            "label": "Sex",
            "default": "All",
            "values": {"All": "All", "Female": "Female", "Male": "Male"},
        },
        "race": {
            "label": "Race", "default": "All Races (includes Hispanic)", "values": {}
        },
        "age": {
            "label": "Age", "default": "All Ages", "values": {}
        },
    },
}
