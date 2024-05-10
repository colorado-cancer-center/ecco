"""
Models derived from disparity index data similar to CDPHE. Note that this
data is about *cancer disparities*, not socioeconomic disparities as in
the CIF data.

See https://github.com/colorado-cancer-center/ecco/issues/27 for details.

Note that since they're all at the county level, we leave out putting
"county" in the name.
"""

from .base import MeasureUnit, MeasuresByCounty

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class CancerDisparitiesIndex(MeasuresByCounty, table=True):
    class Config:
        label = "Cancer Disparities Index"

# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

DISPARITY_INDEX_MODELS = {
    "county": [
        CancerDisparitiesIndex
    ],
    "tract": []
}

DISPARITY_INDEX_MEASURE_DESCRIPTIONS = {
    "cancerdisparitiesindex": {
        "Colorectal Cancer Index": {
            "label": "Colorectal Cancer Index",
            "unit": MeasureUnit.RANK,
        },
        "Lung Cancer Index": {
            "label": "Lung Cancer Index",
            "unit": MeasureUnit.RANK
        },
        "Head and Neck Cancer Index": {
            "label": "Head and Neck Cancer Index",
            "unit": MeasureUnit.RANK,
        },
        "Breast Cancer Index": {
            "label": "Breast Cancer Index",
            "unit": MeasureUnit.RANK,
        },
    }
}
