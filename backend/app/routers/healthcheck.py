"""
API endpoint for '/healthz' healthcheck, which just demonstrates that the API is
up and running.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def healthcheck():
    return {"status": "ok"}
