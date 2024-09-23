import sys

import pytest_asyncio
from fastapi.testclient import TestClient

sys.path.append("/app")

from main import app


@pytest_asyncio.fixture()
async def client():
    with TestClient(app) as c:
        yield c
