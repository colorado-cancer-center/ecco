"""
Models derived from disparity index data similar to CDPHE. Note that this
data is about *cancer disparities*, not socioeconomic disparities as in
the CIF data.

See https://github.com/colorado-cancer-center/ecco/issues/27 for details.

Note that since they're all at the county level, we leave out putting
"county" in the name.
"""

from .base import MeasuresByCounty

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
