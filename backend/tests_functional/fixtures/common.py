import importlib
import os
import sys
from collections.abc import AsyncIterator

import pytest
from aiohttp.test_utils import TestClient, TestServer

from tests_functional.constants import BACKEND_DIR, JWT_TEST_SECRET


@pytest.fixture
def jwt_secret():
    return JWT_TEST_SECRET


@pytest.fixture(scope='session')
def app_module(postgres_dsn: str):
    os.environ['DATABASE_URL'] = postgres_dsn
    os.environ['JWT_SECRET'] = JWT_TEST_SECRET
    os.environ.setdefault('HOST', '127.0.0.1')
    os.environ.setdefault('PORT', '8080')

    sys.path.insert(0, str(BACKEND_DIR))
    config = importlib.import_module('config')
    auth = importlib.import_module('auth')
    app = importlib.import_module('app')

    importlib.reload(config)
    importlib.reload(auth)
    app = importlib.reload(app)

    return app


@pytest.fixture
async def app_client(app_module) -> AsyncIterator[TestClient]:
    app = app_module.create_app()
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()

    yield client

    await client.close()
