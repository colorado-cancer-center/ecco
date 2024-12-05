#!/usr/bin/env python

import itertools
from pprint import pprint
import random
import sys

sys.path.append("/app")

import click
import asyncio

import openpyxl
from openpyxl.utils import get_column_letter

from tqdm import tqdm
from sqlmodel import delete, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine

from models.geom import HealthRegion
from models.vaping import (
    VapingHealthRegion
)


def dummy_data_generator(hs_regions):
    hs_region_ids = list(hs_regions.keys())

    sexes = [
        "All", "Female", "Male"
    ]
    races = [
        "All Races (includes Hispanic)",
        "White", "Black", "Hispanic", "Asian",
        "American Indian/Alaska Native",
        "Native Hawaiian/Other Pacific Islander"
    ]
    ages = [
        "18-24", "25-34", "35-44", "45-54", "55-64", "65+"
    ]

    for region_id in hs_region_ids:
        for age, sex, race in itertools.product(ages, sexes, races):
            yield {
                "hs_region": region_id,
                "FIPS": region_id,
                "State": "Colorado",
                "value": random.random() * 100,
                "sex": sex,
                "race": race,
                "age": age,
            }

async def import_vaping_data(delete_before_import=True):
    """
    TBC: import vaping data, but at the moment we don't know what format
    the input data will be. This function currently fills the
    VapingHealthRegion measure category with a measure called
    'youthvapingrate' and dummy data for the values.
    """

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    # step 1. convert input excel using the column mapper

    # for each file, import it into the database
    async with async_session() as session:
        result = await session.execute(select(HealthRegion))
        hs_regions_list = result.scalars().all()
        
        print(x.keys() for x in hs_regions_list)

        hs_regions = {
            region.hs_region: region.counties
            for region in hs_regions_list
        }
        print(hs_regions)

        # delete all existing entries in the target models
        if delete_before_import:
            for model in (VapingHealthRegion, ):
                result = await session.execute(delete(model))
                tqdm.write(f" - Deleted {result.rowcount} from {model.__name__}")

        title = "Vaping Data"

        # import measure for the current sheet
        meaure_name = "Youth Vaping Rate"
        tqdm.write(f"* Processing {title}, {meaure_name}...")

        # read the column, normalizing sheet cols to internal names
        rows = [
            {
                **row,
            }
            for row in dummy_data_generator(hs_regions)
            if row["value"] is not None
        ]
        
        session.add_all([
            model(**{
                **row,
                "measure": meaure_name
            })
            for row in rows
        ])

        # commit session at the end
        await session.commit()


@click.command()
# @click.argument('excel-sheets', type=str, nargs=-1)
def main():
    asyncio.run(import_vaping_data())

if __name__ == '__main__':
    main()
