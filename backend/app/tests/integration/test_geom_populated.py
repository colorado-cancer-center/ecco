import sys

import pytest

sys.path.append("/app/src")

@pytest.mark.asyncio
async def test_geom_populated(client):
    """
    For each top-level geometry type returned from /stats/measures,
    check that it contains the expected number of entities.
    """

    # first, pull the 'measures' endpoint to get metadata about the measures
    # that we'll use when we issue the queries
    response = client.get("/stats/measures")
    assert response.status_code == 200
    measures = response.json()

    PLURAL_FORM = {
        "county": "counties",
        "tract": "tracts",
        "healthregion": "healthregions",
    }

    for type in measures.keys():
        # query for each geometry type
        path = f"/{PLURAL_FORM[type]}"
        response = client.get(path)

        assert response.status_code == 200, path
        data = response.json()

        # based on the type, check that we have the expected number of geometric
        # entities
        if type == "county":
            assert len(data) == 64
        elif type == "tract":
            assert len(data) == 1249
        elif type == "healthregion":
            assert len(data) == 21
