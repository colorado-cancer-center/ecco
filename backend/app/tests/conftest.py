import pytest

from fastapi.testclient import TestClient

import sys
sys.path.append("/app")

from main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
