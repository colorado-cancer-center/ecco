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
        label = "Vaping"

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
# the key of this dict is the name of the measure in the database,
# and the value is what's displayed as the measure in the UI
QUESTIONS = {
    "youth_vaping_ever": "Pct of students who have ever used an electronic vapor product",
    "youth_vaping_now": "Pct of students who used an electronic vapor product in the past 30 days",
    "adult_vaping_ever": "Pct of adults who have ever used an electronic vapor product",
    "adult_vaping_now": "Pct of adults who currently use an electronic vapor product",
}

# shows up in the 'source' field in the legend when this measure is displayed
# in the UI
QUESTIONS_TO_SOURCES = {
    "youth_vaping_ever": {
        "source": "Healthy Kids Colorado Survey, 2023",
        "source_url": "https://cdphe.colorado.gov/hkcs"
    },
    "youth_vaping_now": {
        "source": "Healthy Kids Colorado Survey, 2023",
        "source_url": "https://cdphe.colorado.gov/hkcs"
    },
    "adult_vaping_ever": {
        "source": "BRFSS, 2023",
        "source_url": "https://www.cdc.gov/brfss/index.html"
    },
    "adult_vaping_now": {
        "source": "BRFSS, 2023",
        "source_url": "https://www.cdc.gov/brfss/index.html"
    },
}

VAPING_MEASURE_DESCRIPTIONS = {
    "vaping": {
        measure_name: {
            "label": question,
            "unit": MeasureUnit.PERCENT,
            **QUESTIONS_TO_SOURCES[measure_name],
        }
        for measure_name, question in QUESTIONS.items()
    }
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
