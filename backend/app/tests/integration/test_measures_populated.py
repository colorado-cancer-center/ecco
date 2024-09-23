import pytest

from urllib.parse import quote_plus

import sys
sys.path.append("/app/src")

from models.base import STATS_MODELS, MEASURE_DESCRIPTIONS
from tools.strings import slug_modelname_sans_type


@pytest.mark.asyncio
async def test_measures_populated(client):
    """
    For each model in MEASURE_DESCRIPTIONS, check that the measure is populated,
    i.e. that it has more than zero rows.
    """
    for type in STATS_MODELS:
        for model in STATS_MODELS[type]:
            simple_model_name = slug_modelname_sans_type(model, type)

            for measure, meta in MEASURE_DESCRIPTIONS[simple_model_name].items():
                # skip county-only measures when testing tracts
                if type == "tract" and meta.get("county_only", False):
                    continue
                # skip tract-only measures when testing counties
                if type == "county" and meta.get("tract_only", False):
                    continue

                encoded_measure = quote_plus(measure)
                path = f"/stats/{type}/{simple_model_name}/fips-value?measure={encoded_measure}"
                response = client.get(path)

                assert response.status_code == 200, path
                data = response.json()

                assert 'values' in data and len(data['values']) > 0, path
