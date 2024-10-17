
import os
import glob
import csv
import re

import pytest

from models.cif_meta import CIF_MEASURE_DESCRIPTIONS

# skip the test if the folder `/data/staging` doesn't exist
needs_cif_staging = pytest.mark.skipif(
    not os.path.exists("/data/staging"),
    reason="Path /data/staging doesn't exist, so can't test CiF data agreement"
)

@needs_cif_staging
def test_cif_metadata_data_agreement():
    """
    Tests that the metadata we have harcoded for the CancerInFocus datasets
    matches the spreadsheets for a specific CIF dataset distribution.
    """

    CIF_DATASHEETS = "/data/staging/2024-10/stats/*_long*.csv"

    sheets = glob.glob(CIF_DATASHEETS)

    # ensure that we have the same number of metadata categories
    # as we do input sheets
    # (we share metadata between county and tract measure categories,
    # so first we have to remove the county/tract specifier, then
    # check if that unique set is the same length as the measure descs)
    # match filenames like this: us_food_desert_tract_long_07-01-2024.csv
    # to extract "food_desert"
    assert (
        len(
            set(
                re.match(r"us_(.*)_(county|tract)_long_.*\.csv", os.path.split(x)[1]).groups()[0]
                for x in sheets
            )
        ) ==
        len(CIF_MEASURE_DESCRIPTIONS)
    )

    SHEETS_TO_MEASURES = {
        "us_cancer_incidence_county": "cancerincidence",
        "us_cancer_mortality_county": "cancermortality",
        "us_economy_county": "economy",
        "us_environment_county": "environment",
        "us_housing_trans_county": "housingtrans",
        "us_rf_and_screening_county": "rfandscreening",
        "us_sociodemographics_county": "sociodemographics",
        "us_disparity_county": "disparities",
        "us_economy_tract": "economy",
        "us_environment_tract": "environment",
        "us_food_desert_tract": "fooddesert",
        "us_housing_trans_tract": "housingtrans",
        "us_rf_and_screening_tract": "rfandscreening",
        "us_sociodemographics_tract": "sociodemographics",
        "us_disparity_tract": "disparities",
    }

    # actual files:
    # 1. us_cancer_incidence_county
    # 2. us_cancer_mortality_county
    # 3. us_economy_county
    # 4. us_environment_county
    # 5. us_housing_trans_county
    # 6. us_rf_and_screening_county
    # 7. us_sociodemographics_county
    # 8. us_disparity_county

    # iterate over each sheet in the CIF_DATASHEETS glob
    for sheet in sheets:
        # isolate just the filename of the sheet using os.path.split
        filename = os.path.split(sheet)[1]

        # if we're looking at tract data, we ignore measure metadata
        # that has the 'county_only' field set to true
        is_tract = "_tract_" in filename

        # skip cancer sheets for now, since we're not using them
        if "cancer" in filename:
            continue

        # read the sheet using the csv.DictReader reader
        with open(sheet, 'r') as f:
            reader = csv.DictReader(f)

            distinct_measures = set()

            if 'cancer' not in sheet:
                # each sheet has these columns:
                # FIPS,County,State,measure,value
                # we're interested in checking that the intersection
                # between the unique values of measure and the 
                for row in reader:
                    distinct_measures.add(row['measure'])
            else:
                # FIPS,County,State,Type,RE,Sex,Site,AAR,AAC
                for row in reader:
                    distinct_measures.add(row['Site'])

            # for some reason CIF adds the month to "Monthly Unemployment Rate"
            # for each release, but we remove it so that it matches our
            # "Monthly Unemployment Rate" metadata entry. we'll remove
            # it here as well so the test passes
            distinct_measures = set(
                re.sub(r"Monthly Unemployment Rate (.*)", "Monthly Unemployment Rate", x)
                for x in distinct_measures
            )

            # also, CIF's tract economoy data doesn't include "Monthly Unemployment Rate"
            # so if we're looking at the tract remove

            # check if a key from SHEETS_TO_MEASURES is in the filename
            # of the sheet
            try:
                model_name = next(
                    v for k, v in SHEETS_TO_MEASURES.items() if k in filename
                )
            except StopIteration:
                raise Exception(f"Could not find model for file {sheet}")

            # skip county-only measures when testing tracts
            # and tract-only measures when testing counties
            # (looking at you 'environment', where the tract data and
            # county data are *completely* different)
            measures = {
                k: v for k, v in
                CIF_MEASURE_DESCRIPTIONS[model_name].items()
                if (
                    is_tract and not v.get("county_only", False) or
                    not is_tract and not v.get("tract_only", False)
                )
            }

            assert set(measures.keys()) == distinct_measures, f"measures mismatch for {sheet} versus model {model_name}"
