#!/usr/bin/env python

import sys
import asyncio
import io
import click
import openpyxl
import csv
import anyio

from itertools import groupby

from sqlalchemy.orm import sessionmaker
from sqlmodel import delete, select
from tqdm import tqdm

sys.path.append("/app")

from db import engine
from models.uccc_responders import UCCCRespondersCounty
from models.geom import County
from sqlalchemy.ext.asyncio import AsyncSession


SHEETS_TO_IMPORT = [
    (2023, "UCCC rsch participants 2023 n=987 for upload.xlsx"),
    (2024, "PRMS.Zipcodes.for.CO.Adult.only - 2024.xlsx"),
    (2025, "UCCC rsch participants 2025 n=1695 for upload.xlsx")
]


def read_sheet(sheet_fp, sheet_name=None):
    """
    Given an Excel sheet, read the data from it and yield
    a dictionary for each row, where the keys are the column
    headers and the values are the cell values.
    """

    wb = openpyxl.load_workbook(sheet_fp)
    ws = wb.active if sheet_name is None else wb[sheet_name]

    # get the header row
    header = [cell.value for cell in ws[1]]

    # get the data rows
    for row in ws.iter_rows(min_row=2, values_only=True):
        yield dict(zip(header, row))

async def import_into_model(session, model, label, records):
    """
    Helper to insert records into model.
    """
    
    tqdm.write(f"* Processing {label}...")
    new_recs = [
        model(**rec)
        for rec in records
    ]
    session.add_all(new_recs)

    tqdm.write(f"* Inserted {len(new_recs)} records")
    tqdm.write("")


async def import_uccc_responser_data(uccc_reponders_sheet, year, async_session):
    """
    Imports health-region uccc_responser data from an Excel sheet into the database.
    """

    # ======================================================================
    # import UCCC responders
    # ======================================================================

    async with async_session() as session:
        # the excel input consists of a single sheet with these three columns:
        # - ZipCode: the zip code of the responder
        # - County: the county of the responder
        # - Urbanicity: the categorical value "Urban" or "Rural"

        # get a dict of county names to FIPS mappings so we don't have to
        # do a ton of queries
        county_fips_results = await session.execute(
            select(County.county, County.us_fips)
        )
        county_to_fips = {
            row[0]: row[1]
            for row in county_fips_results.all()
        }


        sheet_rows = read_sheet(uccc_reponders_sheet)
        # first, sort by county so groupby works
        sorted_rows = sorted(
            sheet_rows,
            key=lambda r: (
                r["County"],
                r["Urbanicity"],
            )
        )
        # then group by county
        grouped_rows = groupby(
            sorted_rows,
            key=lambda r: (
                r["County"],
                r["Urbanicity"],
            )
        )

        instances = [
            {
                "FIPS": county_to_fips[county_name],
                "County": county_name,
                "State": "Colorado",
                "measure": "responses",
                "value": len(list(data)),
                "urbanicity": urbanicity,
                "year": year,
            }
            for (county_name, urbanicity), data in grouped_rows
        ]

        await import_into_model(
            session, UCCCRespondersCounty, "UCCC Responders by County", instances
        )

        # unfortunately, the way factors are currently set up assumes that there
        # will be an 'all' entry in the data that aggregates the other values that
        # that factor can take on. this becomes an issue for datasets that aren't
        # explicitly broken out that way.
        # since our data lacks that (i.e. each zip code is urban/rural based on the
        # county in which it's located), we need to create those 'all' entries
        # ourselves by just adding in each county with urbanicity='All'
        await import_into_model(
            session, UCCCRespondersCounty, "UCCC Responders by County",
            ({ **inst, "urbanicity": "All" } for inst in instances)
        )

        await session.commit()

async def import_uccc_responser_years(uccc_reponders_dir, delete_before_import=True):
    """
    Imports health-region uccc_responser data from a set of Excel files under
    uccc_reponders_dir into the database. Each file corresponds to a year of
    data.
    """

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    if delete_before_import:
        async with async_session() as session:
            print("* Deleting existing UCCC responser data...")
            for model in (UCCCRespondersCounty,):
                result = await session.execute(delete(model))
                print(f" - Deleted {result.rowcount} from {model.__name__}")
            print()
            await session.commit()

    for year, sheet_name in SHEETS_TO_IMPORT:
        async with await anyio.open_file(f"{uccc_reponders_dir}/{sheet_name}", "rb") as uccc_reponders_sheet:
            sheet_bytes = await uccc_reponders_sheet.read()
            await import_uccc_responser_data(io.BytesIO(sheet_bytes), year, async_session)

@click.command()
@click.argument('uccc-reponders-dir', type=click.Path(exists=True))
def main(uccc_reponders_dir):
    asyncio.run(import_uccc_responser_years(
        uccc_reponders_dir
    ))

if __name__ == '__main__':
    main()
