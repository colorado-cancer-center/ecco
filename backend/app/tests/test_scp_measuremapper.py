import pytest

import sys
sys.path.append("/app")

from models.base import MeasureUnit
from models.scp import SCP_MEASURE_DESCRIPTIONS

from tools.collections import MeasureMapper

def test_scp_mapped_measures():
    """
    Spot-check the MeasureMapper objects in SCP_MEASURE_DESCRIPTIONS
    and ensure we're getting the right units back, both via __getitem__()
    and via get().
    """
    for model, mapper in SCP_MEASURE_DESCRIPTIONS.items():
        # ensure that trends give us ordinal values (e.g., falling, stable, rising)
        # and that everything else gives us rates (i.e., incindence, mortality rates per 100k)
        expected_unit = MeasureUnit.ORDINAL if "trend" in model else MeasureUnit.RATE

        assert mapper["All Cancer Sites"]["unit"] is not None
        assert mapper["All Cancer Sites"]["unit"] == expected_unit

        assert mapper["All Cancer Sites"].get("unit") is not None
        assert mapper["All Cancer Sites"].get("unit") == expected_unit

    
def test_measuremapper_immutable():
    """
    Ensure that we can't set items on a MeasureMapper object.
    """
    mapper = MeasureMapper(MeasureUnit.RATE)

    with pytest.raises(TypeError):
        mapper["foo"] = "bar"
    
    with pytest.raises(AttributeError):
        mapper.set("foo", "bar")

def test_measuremapper_stringification():
    """
    Test str/repr methods on MeasureMapper.
    """
    mapper = MeasureMapper(MeasureUnit.RATE)

    assert str(mapper) == "MeasureMapper(default_unit=MeasureUnit.RATE)"
    assert repr(mapper) == "MeasureMapper(default_unit=MeasureUnit.RATE)"
