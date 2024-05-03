from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import  add_pagination

from fastapi_cache import FastAPICache
from fastapi_cache.backends.memcached import MemcachedBackend
import aiomcache

from routers import geometry, statistics

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

# enable caching via fastapi-cache
@app.on_event("startup")
async def startup():
    mc = aiomcache.Client("memcached", 11211)
    FastAPICache.init(MemcachedBackend(mc), prefix="fastapi-cache")

# adds in routers that host geometry, statistics endpoints
app.include_router(geometry.router)
app.include_router(statistics.router)
