import sys
sys.path.append("/app")

from models.base import MeasureUnit
from models.scp import SCP_MEASURE_DESCRIPTIONS

def test_scp_mapped_measures():
    from app.tools.collections import MeasureMapper

    for model, mapper in SCP_MEASURE_DESCRIPTIONS.items():
        # ensure it's dict-like
        assert isinstance(mapper, dict)

        # ensure that trends give us ordinal values (e.g., falling, stable, rising)
        # and that everything else gives us rates (i.e., incindence, mortality rates per 100k)
        expected_unit = MeasureUnit.ORDINAL if "trend" in model else MeasureUnit.RATE
        assert mapper["All Cancer Sites"]["unit"] == expected_unit

    