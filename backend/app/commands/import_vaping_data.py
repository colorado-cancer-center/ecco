#!/usr/bin/env python

import sys
import asyncio
import click
import openpyxl

from sqlalchemy.orm import sessionmaker
from sqlmodel import delete
from tqdm import tqdm

sys.path.append("/app")

from db import engine
from models.vaping import StateYouthVapingStats, VapingHealthRegion
from sqlalchemy.ext.asyncio import AsyncSession


def read_sheet(sheet_fp):
    """
    Given an Excel sheet, read the data from it and yield
    a dictionary for each row, where the keys are the column
    headers and the values are the cell values.
    """

    wb = openpyxl.load_workbook(sheet_fp)
    ws = wb.active

    # get the header row
    header = [cell.value for cell in ws[1]]

    # get the data rows
    for row in ws.iter_rows(min_row=2, values_only=True):
        yield dict(zip(header, row))


def region_rows_to_records(records):
    """
    Takes in rows read from read_sheet() and formats them
    into records that we'll insert into the region-level measures table.

    Unfortunately, the source data is not dense; we don't, for example, have
    records that identify a specific age, gender, and race, so we can't subset
    on each factor independently (e.g., to find how many 16 year olds of a
    specific racial group vape). Instead, we create measures for each
    question+demographic pair, and then populate the "factor" column with the
    demographic value.

    Since we create one measure per question+demographic pair, we need to expand
    the "Total" demographic into one row per other demographic with the value
    "All" for each; this allows us to show a value for each question that's not
    specific to the chosen demographic.

    Finally, we change "RaceID" to "Race" to make displaying the measures in
    the UI a little easier.
    """
    for rec in records:
        # if the demographic is "Total", expand that row into
        # one row per other demographic with the value "All"
        # for each
        if rec["Demographic"] == "Total":
            for demographic in ["Age", "Gender", "Race"]:
                yield {
                    "hs_region": rec["region"],
                    "State": "Colorado",
                    "measure": f"{rec['Health_measure']} - By {demographic}",
                    "factor": f"All",
                    "value": rec["state_percent"] / 100.0 if rec["state_percent"] is not None else None,
                }
        else:
            demographic = rec["Demographic"] if rec["Demographic"] != "RaceID" else "Race"

            # specially remap specific demographics
            if demographic == "Gender":
                factor = rec["population"].removesuffix("-Gender")
            else:
                factor = rec["population"]

            # just yield a single row for other demographics
            yield {
                "hs_region": rec["region"],
                "State": "Colorado",
                "measure": f"{rec['Health_measure']} - By {demographic}",
                "factor": factor,
                "value": rec["state_percent"] / 100.0 if rec["state_percent"] is not None else None,
            }
    
def state_rows_to_records(records):
    """
    Takes in rows read from read_sheet() and formats them
    into records that we'll insert into the state-level measures table.
    """

    for rec in records:
        # only acquire unfactored data; skip the rest
        if rec["Demographic"] != "Total":
            continue

        yield {
            "measure_category": "Youth Vaping",
            "measure": f"{rec['Health_measure']} - Total",
            "state_avg": rec["state_percent"] / 100.0 if rec["state_percent"] is not None else None,
            "us_avg": None,
            "source": "Healthy Kids Colorado Survey, 2023",
        }

async def import_into_model(async_session, model, label, records, delete_before_import=True):
    """
    Helper to insert records into model, clearing the model beforehand if requested.
    """
    async with async_session() as session:
        # delete all existing entries in the target model
        if delete_before_import:
            result = await session.execute(delete(model))
            tqdm.write(f" - Deleted {result.rowcount} rows from {model.__name__}")

        tqdm.write(f"* Processing {label}...")
        new_recs = [
            model(**rec)
            for rec in records
        ]
        session.add_all(new_recs)

        tqdm.write(f"* Inserted {len(new_recs)} records")

        await session.commit()


async def import_vaping_data(regional_sheet, state_sheet, delete_before_import=True):
    """
    Imports health-region vaping data from an Excel sheet into the database.
    """

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # step 1. bring in regional data as measures
    await import_into_model(
        async_session, VapingHealthRegion, "region-level vaping data",
        (
            rec for rec in
            region_rows_to_records(read_sheet(regional_sheet))
            if rec["value"] is not None
        )
    )

    # step 2. bring in state-level data into state table
    await import_into_model(
        async_session, StateYouthVapingStats, "state-level vaping data",
        state_rows_to_records(read_sheet(state_sheet))
    )


@click.command()
@click.argument('regional-sheet', type=click.File('rb'))
@click.argument('state-sheet', type=click.File('rb'))
def main(regional_sheet, state_sheet):
    asyncio.run(import_vaping_data(regional_sheet, state_sheet))

if __name__ == '__main__':
    main()
