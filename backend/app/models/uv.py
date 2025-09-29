"""
Model derived from UV data from UCCC, likely originating from
https://gis.cancer.gov/tools/uv-exposure/.

The current data is watt-hours per meter squared (Wh/m²) aggregated to the
county level.

See https://github.com/colorado-cancer-center/ecco/issues/128 for details.
"""

from .base import MeasureUnit, MeasuresByCounty

# ===========================================================================
# === models from the CDPHE disparity index data
# ===========================================================================

class UVExposureCounty(MeasuresByCounty, table=True):
    class Config:
        label = "UV Exposure"

# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

UV_MODELS = {
    "county": [
        UVExposureCounty
    ],
}

UV_MEASURE_DESCRIPTIONS = {
    "uvexposure": {
        "UV_Wh_m2": {
            "label": "UV Irradiation in Wh/m²",
            "unit": MeasureUnit.RATE,
            "source": "UV Estimates for 2000-2024",
            "source_url": "https://gis.cancer.gov/tools/uv-exposure/",
        },
    }
}
