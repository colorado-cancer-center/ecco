from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Polygon(BaseModel):
    type: str
    coordinates: List[List[List[float]]]
