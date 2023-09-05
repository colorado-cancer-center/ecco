#!/usr/bin/env python

import asyncio
import sys
import click
sys.path.append("/app")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import delete

from db import engine
from models import USState

US_STATES_DATA = [
    { "name": "Alabama", "abbreviation": "AL"},
    { "name": "Alaska", "abbreviation": "AK"},
    { "name": "Arizona", "abbreviation": "AZ"},
    { "name": "Arkansas", "abbreviation": "AR"},
    { "name": "California", "abbreviation": "CA"},
    { "name": "Canal Zone", "abbreviation": "CZ"},
    { "name": "Colorado", "abbreviation": "CO"},
    { "name": "Connecticut", "abbreviation": "CT"},
    { "name": "Delaware", "abbreviation": "DE"},
    { "name": "District of Columbia", "abbreviation": "DC"},
    { "name": "Florida", "abbreviation": "FL"},
    { "name": "Georgia", "abbreviation": "GA"},
    { "name": "Guam", "abbreviation": "GU"},
    { "name": "Hawaii", "abbreviation": "HI"},
    { "name": "Idaho", "abbreviation": "ID"},
    { "name": "Illinois", "abbreviation": "IL"},
    { "name": "Indiana", "abbreviation": "IN"},
    { "name": "Iowa", "abbreviation": "IA"},
    { "name": "Kansas", "abbreviation": "KS"},
    { "name": "Kentucky", "abbreviation": "KY"},
    { "name": "Louisiana", "abbreviation": "LA"},
    { "name": "Maine", "abbreviation": "ME"},
    { "name": "Maryland", "abbreviation": "MD"},
    { "name": "Massachusetts", "abbreviation": "MA"},
    { "name": "Michigan", "abbreviation": "MI"},
    { "name": "Minnesota", "abbreviation": "MN"},
    { "name": "Mississippi", "abbreviation": "MS"},
    { "name": "Missouri", "abbreviation": "MO"},
    { "name": "Montana", "abbreviation": "MT"},
    { "name": "Nebraska", "abbreviation": "NE"},
    { "name": "Nevada", "abbreviation": "NV"},
    { "name": "New Hampshire", "abbreviation": "NH"},
    { "name": "New Jersey", "abbreviation": "NJ"},
    { "name": "New Mexico", "abbreviation": "NM"},
    { "name": "New York", "abbreviation": "NY"},
    { "name": "North Carolina", "abbreviation": "NC"},
    { "name": "North Dakota", "abbreviation": "ND"},
    { "name": "Ohio", "abbreviation": "OH"},
    { "name": "Oklahoma", "abbreviation": "OK"},
    { "name": "Oregon", "abbreviation": "OR"},
    { "name": "Pennsylvania", "abbreviation": "PA"},
    { "name": "Puerto Rico", "abbreviation": "PR"},
    { "name": "Rhode Island", "abbreviation": "RI"},
    { "name": "South Carolina", "abbreviation": "SC"},
    { "name": "South Dakota", "abbreviation": "SD"},
    { "name": "Tennessee", "abbreviation": "TN"},
    { "name": "Texas", "abbreviation": "TX"},
    { "name": "Utah", "abbreviation": "UT"},
    { "name": "Vermont", "abbreviation": "VT"},
    { "name": "Virgin Islands", "abbreviation": "VI"},
    { "name": "Virginia", "abbreviation": "VA"},
    { "name": "Washington", "abbreviation": "WA"},
    { "name": "West Virginia", "abbreviation": "WV"},
    { "name": "Wisconsin", "abbreviation": "WI"},
    { "name": "Wyoming", "abbreviation": "WY"},
]

async def populate():
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        result = await session.execute(delete(USState))
        click.echo(f"Deleted {result.rowcount} rows")

        for state in US_STATES_DATA:
            session.add(USState(**state))

        click.echo(f"Inserted {len(US_STATES_DATA)} rows")

        await session.commit()

@click.command()
def main():
    asyncio.run(populate())

if __name__ == "__main__":
    main()
