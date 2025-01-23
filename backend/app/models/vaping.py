"""
Model derived from youth vaping data for CO health regions, collections of
counties for which specific data is tracked.

More about health regions can be found here:
https://www.arcgis.com/home/item.html?id=75e32548d3b24169adb942ecb7424937

See https://github.com/colorado-cancer-center/ecco/issues/105 for details about
this model and its inclusion in ECCO.
"""

from sqlmodel import Field

from .base import BaseStatsModel, MeasureUnit, MeasuresByHealthRegion

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class VapingHealthRegion(MeasuresByHealthRegion, table=True):
    class Config:
        label = "Youth Vaping"

    # since we only have data for one factor per measure, we can't compare, e.g.
    # sex vs race; instead, we define a generic 'factor' field that differs
    # depending on the measure; e.g., "Percentage of ... used vaping product - Age"
    # would define the factor as the age group
    factor: str = Field(nullable=True, index=True)

    @classmethod
    def get_factors(cls):
        return (cls.factor, )


# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

VAPING_MODELS = {
    "healthregion": [
        VapingHealthRegion
    ]
}

# the questions from the source data (i.e., "Health_measure" column)
QUESTIONS = [
    "Percentage of students who have ever used an electronic vapor product",
    "Percentage of students who used an electronic vapor product in the past 30 days",
]

# these are the values of the "Demographic" column in the source data; at
# import, we create one measure per question+demographic pair.
# (the special demographic "Total" is expanded into one row per other
# demographic at the time of import, so we don't deal with it here)
FACTOR_FIELDS = [
    "Age",
    "Gender",
    "Race",
]

VAPING_MEASURE_DESCRIPTIONS = {
    "vaping": {
        f"{question} - By {factor}": {
            "label": f"{question} - By {factor}",
            "unit": MeasureUnit.PERCENT,
        }
        for question in QUESTIONS
        for factor in FACTOR_FIELDS
    }
}

VAPING_FACTOR_DESCRIPTIONS = {
    "vaping": {
        "factor": {
            "label": "Filter",
            "default": "All",
            "values": {
                "All": "All",
                "SE Asian": "Southeast Asian",
                "SA": "South Asian",
                "AIAN": "American Indian or Alaska Native",
                "NHPI": "Native Hawaiian or Pacific Islander",
            },
        },
    },
}

# ===========================================================================
# === state-level data models
# ===========================================================================

class StateYouthVapingStats(BaseStatsModel, table=True):
    # measure category, similar to CiF
    measure_category: str = Field(index=True)

    # measure
    measure: str = Field(index=True)

    # core statistics
    state_avg: float = Field()
    us_avg: float = Field(nullable=True, default=None)

    # metadata
    source: str = Field(nullable=True, default=None)

    class Config:
        label = "State Youth Vaping Statistics"
