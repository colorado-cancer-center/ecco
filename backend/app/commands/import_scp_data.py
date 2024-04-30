#!/usr/bin/env python

import csv
from pathlib import Path
import sys

sys.path.append("/app")

import click
import asyncio

from tqdm import tqdm
from sqlmodel import delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine

from models.scp import (
    SCPDeathsCounty, SCPIncidenceCounty
)

# the FIPS code for Colorado
STATE_CO_FIPS = 8

# optional suffix for SCP data that's filtered to,
# .e.g, a state FIPS
# STATE_FIPS_SUFFIX = "_state08"
STATE_FIPS_SUFFIX = ""

# filenames under the SCP folder to process
INPUT_FILES = [
    f'state_cancer_profiles_death{STATE_FIPS_SUFFIX}.csv',
    f'state_cancer_profiles_incidence{STATE_FIPS_SUFFIX}.csv',
]

# mapping from input filenames to model classes
# and model-specific metadata
FILENAMES_TO_MODELS_AND_META = {
    f"state_cancer_profiles_death{STATE_FIPS_SUFFIX}.csv": {
        "model": SCPDeathsCounty,
        "aac_col": "average_annual_count",
        "aar_col": "age_adjusted_death_raterate_note___deaths_per_100_000"
    },
    f"state_cancer_profiles_incidence{STATE_FIPS_SUFFIX}.csv": {
        "model": SCPIncidenceCounty,
        "aac_col": "average_annual_count",
        "aar_col": "age_adjusted_incidence_raterate_note___cases_per_100_000"
    }
}

class ModelNotProvidedException(Exception):
    """
    Raised when an input file is found that has no associated
    model class.
    """
    pass

def co_county_rows(csv_file:Path):
    """
    Yields rows from the input CSV file that are for Colorado counties.
    """
    with open(csv_file, 'r') as fp:
        reader = csv.DictReader(fp)

        for row in reader:
            if int(row['state_fips']) != STATE_CO_FIPS or row['locale_type'] != "county":
                continue
            yield row

async def import_scp_dataset(model, csv_path:Path, aac_col: str, aar_col:str, delete_before_import:bool=True):
    """
    Imports SCP data into the database.

    If delete_before_import is True, all existing entries in the target model
    are deleted before importing.
    """

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # step 1. convert input excel using the column mapper

    # for each file, import it into the database
    async with async_session() as session:
        tqdm.write(f"* About to process {csv_path} for model {model.__name__}...")

        # delete all existing entries in the target model
        if delete_before_import:
            result = await session.execute(delete(model))
            tqdm.write(f" - Deleted {result.rowcount} from {model.__name__}")

        # count the rows so we can display a progress bar
        row_count = sum(1 for _ in co_county_rows(csv_path))

        # read each row, creating an object from it and adding it to the list
        obj_list = []
        
        for row in tqdm(co_county_rows(csv_path), total=row_count, desc=f"Processing {csv_path}"):
            # create a new object
            obj_list.append(model(**{
                "FIPS" : row["fips"],
                "County" : row["county"].replace(", Colorado", "").replace(" (8)", ""),
                "State" : "Colorado",

                # cancer-specific values
                "Site" : row["cancer"],
                "AAR": row[aar_col],
                "AAC": row[aac_col],

                # factor columns
                "sex": row["sex"].replace("Both Sexes", "All"),
                "stage": row["stage"],
                "race": row["race"],
                "age": row["age"],

                # trend column, for 'trend' view-like models
                "trend": row["recent_trend"]
            }))

        # bulk insert all objects
        session.add_all(obj_list)

        # commit session at the end
        await session.commit()

async def import_all_files(folder):
    for input_file in INPUT_FILES:
        try:
            meta = FILENAMES_TO_MODELS_AND_META[input_file]
        except KeyError:
            raise ModelNotProvidedException(f"No model matching input file '{input_file}'")
    
        csv_path = Path(folder, input_file).resolve()
        await import_scp_dataset(
            model=meta['model'], csv_path=csv_path,
            aac_col=meta['aac_col'], aar_col=meta['aar_col']
        )

@click.command()
@click.argument('scp-csv-folder', type=str)
def main(scp_csv_folder):
    asyncio.run(import_all_files(scp_csv_folder))

if __name__ == '__main__':
    main()
