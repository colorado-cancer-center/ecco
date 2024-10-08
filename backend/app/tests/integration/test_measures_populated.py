import pytest

from urllib.parse import quote_plus

import sys

from models.scp import SCP_CANCER_MODELS
from tools.collections import MeasureMapper
sys.path.append("/app/src")

from models.base import STATS_MODELS, MEASURE_DESCRIPTIONS, MeasureUnit
from tools.strings import slug_modelname_sans_type


@pytest.mark.asyncio
async def test_measures_populated(client):
    """
    For each model in MEASURE_DESCRIPTIONS, check that the measure is populated,
    i.e. that it has more than zero rows.
    """

    # first, pull the 'measures' endpoint to get metadata about the measures
    # that we'll use when we issue the queries
    response = client.get("/stats/measures")
    assert response.status_code == 200
    measures = response.json()

    for type in STATS_MODELS:
        for model in STATS_MODELS[type]:
            simple_model_name = slug_modelname_sans_type(model, type)

            for measure, meta in MEASURE_DESCRIPTIONS[simple_model_name].items():
                # retrieve metadata about the factors for the given model+type
                factor_meta = (
                    measures[type]["categories"]
                        .get(simple_model_name, {})
                        .get("measures", {})
                        .get(measure, {})
                        .get("factors")
                )

                # skip county-only measures when testing tracts
                if type == "tract" and meta.get("county_only", False):
                    continue
                # skip tract-only measures when testing counties
                if type == "county" and meta.get("tract_only", False):
                    continue

                # ==============================================================================================
                # === resolve factor values that will produce data
                # ==============================================================================================

                # the following figures out what factors are populated for
                # measures that have factors and use those in the query. (for
                # example, Site="Breast (Female)" will produce no results when
                # querying without specifying the sex, since it will default to
                # sex="All")

                # if there are factors for the current model, query for values
                # of those factors that we know will produce results, preferring
                # the factor's default value if multiple options exist.
                # if that's not possible (e.g., if there's no data at all), just
                # query for the default values.
                factors = None

                print(model.get_factors())
                print(str(factor_meta))

                if len(model.get_factors()) > 0 and factor_meta is not None:
                    # get populated value options for each factor
                    factor_values = {}

                    for factor_field in model.get_factors():
                        # factor field names are in the form of "model.field"
                        factor = str(factor_field).split(".")[-1]
                        factor_opts = list(factor_meta[factor].get("values", {}).keys())

                        # use the default if it's populated, otherwise use the first value
                        factor_values[factor] =  (
                            factor_meta[factor]["default"]
                            if factor_meta[factor]["default"] in factor_opts or len(factor_opts) == 0 else
                            factor_opts[0]
                        )

                    # construct a querystring arg for the chosen factor values
                    factors = [
                        f"{factor}:{factor_values[factor]}"
                        for factor in factor_values
                    ]

                # ==============================================================================================
                # === perform query for the measure
                # ==============================================================================================

                encoded_measure = quote_plus(measure)
                path = f"/stats/{type}/{simple_model_name}/fips-value?measure={encoded_measure}"

                if factors is not None:
                    path += "&filters=" + quote_plus(";".join(factors))

                response = client.get(path)

                assert response.status_code == 200, path
                data = response.json()

                assert "values" in data and len(data["values"]) > 0, path

def test_measuremapper_scp_model_populated():
    """
    Test that we can set a model on a MeasureMapper object and then query
    it to get measures. We'd ordinarily hardcode the measures in the metadata,
    but in this case the measures might change so we reflect it from the data.

    Note that this requires a database populated with the SCP data, so
    it's technically an integration test.
    """

    for model in SCP_CANCER_MODELS:
        mapper = MeasureMapper(MeasureUnit.RATE, model=model, measure_column="Site")

        test_measure = "All Cancer Sites"

        # see that our key accesses recapitulate the received keys
        assert mapper[test_measure]["unit"] == MeasureUnit.RATE
        assert mapper[test_measure]["label"] == test_measure

        # check that we're seeing greater than zero elements
        assert len([x for x in mapper]) > 0
