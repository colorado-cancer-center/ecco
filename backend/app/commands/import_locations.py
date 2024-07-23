#!/usr/bin/env python

import asyncio
import json
import sys
import click
sys.path.append("/app")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import delete

from db import engine
from models import LocationCategory, Location

from tools.strings import slugify

async def populate_locations(location_categories, locations):
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        # delete the locations, then the categories
        result = await session.execute(delete(Location))
        click.echo(f"Deleted {result.rowcount} location rows")
        result = await session.execute(delete(LocationCategory))
        click.echo(f"Deleted {result.rowcount} location-category rows")

        for category_name, items in location_categories.items():
            # create and add the category to the transaction, so we can
            # reference it when creating the items that belong to it
            category = LocationCategory(
                id=slugify(category_name),
                name=category_name
            )
            session.add(category)

            # create each item in the category
            for item_name, item_id in items.items():
                location = Location(
                    id=item_id,
                    name=item_name,
                    category=category,
                    # geometry_json=json.dumps(locations[item_id])
                    geometry_json=locations[item_id]
                )
                session.add(location)

        click.echo(f"Inserted {len(location_categories)} rows")

        await session.commit()

# takes two required params, the path to locations.json and locations-data.json
@click.command()
@click.argument('location-categories-path', type=str)
@click.argument('location-data-path', type=str)
def main(location_categories_path, location_data_path):
    # load location categories, location data
    with open(location_categories_path, 'r') as f:
        location_categories = json.load(f)
    with open(location_data_path, 'r') as f:
        locations = json.load(f)

    # populate database with categories and locations
    asyncio.run(populate_locations(location_categories, locations))

if __name__ == "__main__":
    main()
