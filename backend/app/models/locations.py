"""
Models that represent entities of interest, e.g. points and polygons,
that can be overlaid on the map. These supplement rather than replace
the county and tract maps.

Since these originally come from GeoJSON, we store the GeoJSON
geometry as jsonb blobs rather than trying to normalize it.
"""

from typing import Any

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Relationship

class LocationCategory(SQLModel, table=True):
    id: str = Field(index=True, primary_key=True)
    name: str = Field(index=True)

    locations: list["Location"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"cascade": "delete"}
    )


class Location(SQLModel, table=True):
    id: str = Field(index=True, primary_key=True)

    # each location belongs to a location category
    # (locations are removed when its parent category is removed)
    category_id: str = Field(foreign_key="locationcategory.id", index=True)
    category: LocationCategory = Relationship(back_populates="locations")

    # FIXME: the following column def is how geometry should be represented
    # in postgis, but ST_GeomFromGeoJSON doesn't support FeatureCollections
    # or Features, just individual geometries. So we'll store the whole
    # feature collection as a jsonb blob instead.

    # # geojson data
    # geometry: Any = Field(
    #     sa_column=Column(
    #         Geometry(
    #             srid=4326,
    #             from_text="ST_GeomFromGeoJSON",
    #             name="geometry",
    #             _spatial_index_reflected=True
    #         )
    #     )
    # )

    geometry_json: dict = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    # # Needed for Column(JSON)
    # class Config:
    #     arbitrary_types_allowed = True
