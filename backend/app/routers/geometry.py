"""
API endpoints that return geometry, e.g. county/tract boundaries.
"""

from fastapi import Depends
from fastapi_cache.decorator import cache
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session

from models import (
    County,
    Tract,
    HealthRegion,
)
from fastapi import APIRouter

router = APIRouter()


# ============================================================================
# === geometry routes
# ============================================================================

@router.get("/counties", response_model=list[County])
@cache()
async def get_counties(session: AsyncSession = Depends(get_session)):
    """
    Returns metadata and geometry for counties. The geometry itself is in the
    `wkb_geometry` subkey for each element and is in JSON-encoded GeoJSON
    format.
    """
    result = await session.execute(select(County))
    counties = result.scalars().all()
    return counties

@router.get("/tracts", response_model=list[Tract])
@cache()
async def get_tracts(session: AsyncSession = Depends(get_session)):
    """
    Returns metadata and geometry for tracts. The geometry itself is in the
    `wkb_geometry` subkey and is in JSON-encoded GeoJSON format.
    """
    result = await session.execute(select(Tract))
    tracts = result.scalars().all()
    return tracts

@router.get("/healthregions", response_model=list[HealthRegion])
@cache()
async def get_healthregions(session: AsyncSession = Depends(get_session)):
    """
    Returns metadata and geometry for health regions, combinations of counties
    for which specific data is tracked. The geometry itself is in the
    `wkb_geometry` subkey and is in JSON-encoded GeoJSON format.
    """
    result = await session.execute(select(HealthRegion))
    healthregions = result.scalars().all()
    return healthregions

# @router.get("/edds", response_model=list[Tract])
# async def get_tracts(session: AsyncSession = Depends(get_session)):
#     """
#     Returns metadata and geometry for economic development districts (EDDs),
#     which are groupings of counties. The geometry itself is in the
#     `wkb_geometry` subkey for each element and is in JSON-encoded GeoJSON
#     format.
#     """
#     result = await session.execute(select(Tract))
#     tracts = result.scalars().all()
#     return tracts
