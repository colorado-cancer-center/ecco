"""
API endpoints that return locations, e.g. cancer treatment centers
and legislative district maps.
"""

from fastapi import Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session

from models import (
    LocationCategory,
    Location
)
from fastapi import APIRouter

router = APIRouter()


# ============================================================================
# === location routes
# ============================================================================

@router.get("/locations", response_model=dict[str, dict[str, str]])
async def get_location_categories(session: AsyncSession = Depends(get_session)):
    """
    Returns all location categories and IDs to associated locations.
    """
    result = await session.execute(select(LocationCategory).join(Location))
    location_categories = result.unique().scalars().all()
    
    # formulate a response that resemebles the frontend locations.json,
    # i.e. a dictionary with category names as keys and a nested dict of values.
    # the nested dict has human-readable labels as keys and location IDs
    # as values.

    response = {
        category.name: {
                location.name: location.id
                for location in category.locations
        }
        for category in location_categories
    }

    return response

@router.get("/locations/by-category/{category_id}", response_model=list[Location])
async def get_locations(category_id: str, session: AsyncSession = Depends(get_session)):
    """
    Returns all locations for a given category. The geometry itself is in the
    geometry_json field and is represented as a GeoJSON FeatureCollection.
    """
    # pull up the category matching category_id
    result = await session.execute(select(LocationCategory).where(LocationCategory.id == category_id))
    category = result.scalars().first()

    # pull all locations that match that category
    result = await session.execute(select(Location).where(Location.category == category))
    locations = result.scalars().all()

    return locations

@router.get("/locations/{item_id}", response_model=Location)
async def get_location_by_id(item_id: str, session: AsyncSession = Depends(get_session)):
    """
    Returns specific locations by ID. The geometry itself is in the
    geometry_json field and is represented as a GeoJSON FeatureCollection.
    """

    # pull one location that matches the requested ID
    result = await session.execute(select(Location).where(Location.id == item_id))
    locations = result.scalars().one()

    return locations
