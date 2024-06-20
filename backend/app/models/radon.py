"""
Model derived from radon data from CDPHE. The data comes from
https://coepht.colorado.gov/radon-data, specifically the spreadsheet
on that page. Radon data is available at both the county and tract level.

In our model, we only include the count and percent of tests for each region
that are above the radon action level, 4 pCi/L.

See https://github.com/colorado-cancer-center/ecco/issues/24 for details.
"""

from .base import MeasureUnit, MeasuresByCounty, MeasuresByTract

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class RadonCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Radon Exposure"

class RadonTract(MeasuresByTract, table=True):
    class Config:
        label = "Radon Exposure"

# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

RADON_MODELS = {
    "county": [
        RadonCounty
    ],
    "tract": [
        RadonTract
    ]
}

RADON_MEASURE_DESCRIPTIONS = {
    "radon": {
        "PctOver4": {
            "label": "Percentage of Tests over 4 pCi/L",
            "unit": MeasureUnit.PERCENT,
        },
        "NTests": {
            "label": "Total Tests",
            "unit": MeasureUnit.COUNT,
        },
        "NTestsover4": {
            "label": "Total Tests over 4 pCi/L",
            "unit": MeasureUnit.COUNT,
        },
    }
}
