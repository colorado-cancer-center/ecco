#!/usr/bin/env python

import csv
import sys
sys.path.append("/app")

import click
import asyncio

from typing import get_type_hints

from tqdm import tqdm
from sqlmodel import delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from settings import LIMIT_TO_STATE

from db import engine
from models import (
    CancerIncidenceCounty,
    CancerMortalityCounty,
    EconomyCounty,
    EnvironmentCounty,
    HousingTransCounty,
    RfAndScreeningCounty,
    SociodemographicsCounty,
    EconomyTract,
    EnvironmentTract,
    FoodDesertTract,
    HousingTransTract,
    RfAndScreeningTract,
    SociodemographicsTract
)

SHEETS_TO_TYPES = {
    "us_cancer_incidence_county": CancerIncidenceCounty,
    "us_cancer_mortality_county": CancerMortalityCounty,
    "us_economy_county": EconomyCounty,
    "us_environment_county": EnvironmentCounty,
    "us_housing_trans_county": HousingTransCounty,
    "us_rf_and_screening_county": RfAndScreeningCounty,
    "us_sociodemographics_county": SociodemographicsCounty,
    "us_economy_tract": EconomyTract,
    "us_environment_tract": EnvironmentTract,
    "us_food_desert_tract": FoodDesertTract,
    "us_housing_trans_tract": HousingTransTract,
    "us_rf_and_screening_tract": RfAndScreeningTract,
    "us_sociodemographics_tract": SociodemographicsTract
}

class ModelForFileNotFoundException(Exception):
    """
    Raised when an input file is found that has no associated
    model class.
    """
    pass

async def import_file(file, session, model=None, delete_before_import=True, dont_limit_states=False):
    """
    Imports a single CSV file via the SQLModel 'model' into the database.

    If model is None, the model is looked up from SHEETS_TO_TYPES, where
    each key is a substring of the filename. If model is not None, the
    model is used directly.

    If delete_before_import is True, all existing entries in the target model
    are deleted before importing. 
    """

    # get entry from SHEETS_TO_TYPES matching filename
    if model is None:
        for file_part, candidate in SHEETS_TO_TYPES.items():
            if file_part in file:
                model = candidate
                break
        else:
            raise ModelForFileNotFoundException(
                f"Could not find model for file {file}"
            )

    # delete all existing entries in the target model
    if delete_before_import:
        result = await session.execute(delete(model))
        tqdm.write(f" - Deleted {result.rowcount} from {model.__name__}")

    field_types = get_type_hints(model)

    with open(file, "r") as fp:
        # read lines using dictreader
        reader = csv.DictReader(fp)

        # read each line, creating an object from it and adding it to the list
        obj_list = []
        for row in reader:
            # create a new object
            obj = model()

            # see if we should skip based on state
            if not dont_limit_states and "State" in row and row["State"] != LIMIT_TO_STATE:
                continue

            # set each value
            for name, value in row.items():
                # perform casts for numeric types
                if field_types[name] in (int, float):
                    if type(value) is str and value.strip() == "" or "NOS" in value:
                        value = 0
                    value = field_types[name](value)

                setattr(obj, name, value)
                obj_list.append(obj)

        # bulk insert all objects
        session.add_all(obj_list)


async def import_us_data(data_folder, dont_limit_states=False, warn_on_missing_model=False):
    """Imports all *_long_*.csv files from the KYS data folder into the database."""

    # get a list of all files in data_folder with filename matching *_long_*.csv
    import glob
    import os

    files = glob.glob(
        os.path.join(data_folder, "*_long_*.csv")
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # for each file, import it into the database
    async with async_session() as session:
        for file in tqdm(files, file=sys.stdout):
            tqdm.write(f"* About to import {file}...")
            
            try:
                await import_file(
                    file, session,
                    dont_limit_states=dont_limit_states
                )
            except ModelForFileNotFoundException as ex:
                if warn_on_missing_model:
                    tqdm.write(f"Warning: {ex}")
                else:
                    raise ex
                
            tqdm.write(f"...insert done, committing...")
            await session.commit()
            tqdm.write(f"done!\n")

        # commit session at the end
        await session.commit()

@click.command()
@click.argument('data-folder', type=click.Path(exists=True))
@click.option('--dont-limit-states', type=bool, default=False,
    help="If specified, will import everything; i.e. it won\'t filter to LIMIT_TO_STATE from settings"
)
@click.option('--warn-on-missing-model', type=bool, default=False,
    help="If specified, will only print a warning (rather than exit) if a model isn't found for a given input file"
)
def main(data_folder, dont_limit_states=False, warn_on_missing_model=False):
    asyncio.run(import_us_data(data_folder, dont_limit_states, warn_on_missing_model))

if __name__ == '__main__':
    main()
