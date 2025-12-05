import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import  add_pagination

from fastapi_cache import FastAPICache
from fastapi_cache.backends.memcached import MemcachedBackend
import aiomcache

from routers import healthcheck, geometry, locations, statistics

from tools.caching import request_key_builder

from settings import IS_DEV, FRONTEND_DOMAIN

# we'll just allow all origins for the time being
ALLOW_ALL_ORIGINS = True

# ============================================================================
# === configuration
# ============================================================================

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8001",
    f"https://{FRONTEND_DOMAIN}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if (not IS_DEV and not ALLOW_ALL_ORIGINS) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# enables pagination plugin
add_pagination(app)

class HealthCheckFilter(logging.Filter):
    def __init__(self, filtered_path: str = "/healthz"):
        super().__init__()
        self.filtered_path = filtered_path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self.filtered_path) == -1

# enable caching via fastapi-cache
@app.on_event("startup")
async def startup():
    mc = aiomcache.Client("memcached", 11211)
    FastAPICache.init(
        MemcachedBackend(mc), prefix="fastapi-cache",
        key_builder=request_key_builder,
    )

    # Remove /healthcheck from access logs
    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())


# adds in routers that host geometry, statistics endpoints
app.include_router(healthcheck.router)
app.include_router(geometry.router)
app.include_router(locations.router)
app.include_router(statistics.router)
