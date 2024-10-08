import pytest

from urllib.parse import quote_plus

import sys
sys.path.append("/app/src")

from models.base import STATS_MODELS, MEASURE_DESCRIPTIONS
from tools.strings import slug_modelname_sans_type


@pytest.mark.asyncio(loop_scope='function')
async def test_fips_vs_bycounty(event_loop, client):
    """
    Test that the values we get from the fips-value endpoint for a county
    match what the by-county endpoint is returning.
    """

    # we're just testing counties here, since we don't have a by-tract endpoint
    type = "county"

    # remember by-county data so we don't have to re-query it
    by_county_data = {}

    for model in STATS_MODELS["county"]:
        simple_model_name = slug_modelname_sans_type(model, type)

        for measure, meta in MEASURE_DESCRIPTIONS[simple_model_name].items():
            # skip tract-only measures when testing counties
            if type == "county" and meta.get("tract_only", False):
                continue

            encoded_measure = quote_plus(measure)
            path = f"/stats/{type}/{simple_model_name}/fips-value?measure={encoded_measure}"
            response = client.get(path)

            assert response.status_code == 200, path
            summary_fips_data = response.json()

            # first check that there's anything to compare
            # assert 'values' in summary_fips_data and len(summary_fips_data['values']) > 0, path

            # for each county FIPS in the fips-value response, query the
            # by-county endpoint and compare the returned values
            for fips in summary_fips_data['values'].keys():
                # after this runs, 'county_data' will either have been populated
                # via a query or populated from the cache
                if fips not in by_county_data:
                    path = f"/stats/by-county/{fips}"
                    response = client.get(path)
                    assert response.status_code == 200, path
                    county_data = response.json()
                    by_county_data[fips] = county_data
                else:
                    county_data = by_county_data[fips]

                # retrieve the fips-value data for the current county
                fips_set_value = summary_fips_data["values"][fips]["value"]
                # retrieve by-county data for the current measure
                try:
                    county_measure_value = county_data["categories"][simple_model_name]["measures"][measure]["value"]
                except KeyError:
                    # raise Exception(f"Missing {simple_model_name}:{measure} in by-county data (FIPS: {fips})")
                    
                    # we're skipping b/c some counties just don't have certain
                    # measures for example, 08057 (jackson county) has no
                    # `trend` values for `scpdeaths`, and since we require trend
                    # != '' for the by-county endpoint, we don't get anything
                    # back and the dict ref above would fail.
                    print(f"Skipping {simple_model_name}:{measure} in by-county data (FIPS: {fips}) since it doesn't exist")
                    continue

                # print(f"Comparing for FIPS {fips} {simple_model_name}/{measure}: county value {county_measure_value} vs. fips-value {fips_set_value}")

                # ensure that it matches the fips-value data
                assert county_measure_value == fips_set_value, f"Mismatch for FIPS {fips} {simple_model_name}/{measure}: county value {county_measure_value} != fips-value {fips_set_value}"
