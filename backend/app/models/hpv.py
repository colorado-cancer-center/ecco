"""
Model derived from HPV immunization data from CDPHE. The data was manually
downloaded from
https://cohealthviz.dphe.state.co.us/t/DCEED_Public/views/CountyRateMaps-Storyboard/CountyRateMapsCombined,
specifically the "Download Data" button on the immunization maps tab. More
immunization records were available, but we're only concerned here with teen HPV
immunizations.

See https://github.com/colorado-cancer-center/ecco/issues/35 for details.
"""

from sqlmodel import Field

from .base import MeasureUnit, MeasuresByCounty

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class HPVCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Teen HPV Immunization Rate"

    # pulled out for use as factors
    sex: str = Field(nullable=True, index=True)

    @classmethod
    def get_factors(cls):
        return (cls.sex, )


# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

HPV_MODELS = {
    "county": [
        HPVCounty
    ]
}

HPV_MEASURE_DESCRIPTIONS = {
    "hpv": {
        "Up-To-Date Percent": {
            "label": "Up-To-Date Percent",
            "unit": MeasureUnit.PERCENT,
        }
    }
}

# for now, deaths and incidence share the same data
HPV_FACTOR_DESCRIPTIONS = {
    "hpv": {
        "sex": {
            "label": "Sex",
            "default": "All",
            "values": {"All": "All", "Female": "Female", "Male": "Male"},
        },
    },
}
