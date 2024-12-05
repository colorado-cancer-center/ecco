"""
Models that represent regions, e.g. the US States, and/or geometry, e.g. county
and tract boundaries
"""

from typing import Any

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


# ===========================================================================
# === models from shapefiles produced by ogr2ogr
# === (they're defined here for use by the API, but explicitly excluded from
# === alembic migrations since we create and load them with ogr2ogr)
# ===========================================================================

class GeometryTable(SQLModel):
    ogc_fid: int = Field(primary_key=True, nullable=False)
    objectid: int = Field(unique=True, index=True)
    wkb_geometry: Any = Field(
        sa_column=Column(
            Geometry(
                srid=4326,
                from_text='ST_GeomFromEWKT',
                name='geometry',
                _spatial_index_reflected=True
            )
        )
    )

    class Config:
        skip_autogenerate = True
        arbitrary_types_allowed = True
        json_encoders = {
            WKBElement: lambda x: to_geojson(to_shape(x))
        }


class County(GeometryTable, table=True):
    __tablename__ = "county"
    county: str = Field(index=True)
    full: str
    label: str
    cnty_fips: str = Field(index=True)
    num_fips: int = Field(index=True)
    cent_lat: float
    cent_long: float
    us_fips: str = Field(index=True)


class Tract(GeometryTable, table=True):
    __tablename__ = "tract"

    # state: Optional[str] = Field(default="Colorado")
    fips: str = Field(index=True)


class HealthRegion(GeometryTable, table=True):
    __tablename__ = "healthregion"

    # an identifier for the health region
    # (it's technically an int, but we keep it a string to match the other
    # geometry tables, in which the identifiers should absolutely be strings)
    hs_region: str = Field(index=True)

    # a comma-delimited list of counties that are in this health region
    counties: str = Field(index=True)


# ===========================================================================
# === reference tables
# ===========================================================================

class USState(SQLModel, table=True):
    __tablename__ = "us_state"

    name : str = Field(index=True, primary_key=True)
    abbreviation : str = Field(index=True)
