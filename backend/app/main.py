from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import  add_pagination

from routers import geometry, statistics

# ============================================================================
# === configuration
# ============================================================================

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# enables pagination plugin
add_pagination(app)

# adds in routers that host geometry, statistics endpoints
app.include_router(geometry.router)
app.include_router(statistics.router)
