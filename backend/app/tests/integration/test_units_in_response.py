import pytest

from urllib.parse import quote_plus

import sys
sys.path.append("/app/src")

from models.base import STATS_MODELS, MEASURE_DESCRIPTIONS
from tools.strings import slug_modelname_sans_type


@pytest.mark.asyncio(loop_scope='function')
async def test_unit_in_response(event_loop, client):
    for type in STATS_MODELS:
        for model in STATS_MODELS[type]:
            simple_model_name = slug_modelname_sans_type(model, type)

            for measure, meta in MEASURE_DESCRIPTIONS[simple_model_name].items():
                encoded_measure = quote_plus(measure)
                path = f"/stats/{type}/{simple_model_name}/fips-value?measure={encoded_measure}"
                response = client.get(path)

                assert response.status_code == 200, path
                data = response.json()

                assert 'unit' in data
                assert data['unit'] is not None and data['unit'] == meta['unit'].value
