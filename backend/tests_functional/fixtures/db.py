import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import suppress

import asyncpg
import pytest
from testcontainers.postgres import PostgresContainer

from tests_functional.constants import SCHEMA_PATH


@pytest.fixture(scope='session')
async def postgres_dsn() -> AsyncIterator[str]:
    # os.environ['DOCKER_HOST'] = 'unix:///Users/v.pereverza/.colima/default/docker.sock'
    os.environ.setdefault('TESTCONTAINERS_RYUK_DISABLED', 'true')
    env_dsn = os.getenv('TEST_DATABASE_URL') or os.getenv('PYTEST_DATABASE_URL')
    if env_dsn:
        yield env_dsn
        return

    with PostgresContainer('postgres:16-alpine', driver=None) as postgres:
        dsn = postgres.get_connection_url()

        ready = False
        for _ in range(30):
            with suppress(Exception):
                conn = await asyncpg.connect(dsn, ssl=False)
                await conn.close()
                ready = True
                break
            await asyncio.sleep(1)

        if not ready:
            raise RuntimeError(f'Postgres did not become ready: {dsn}')

        yield dsn


@pytest.fixture(scope='session')
async def raw_db_pool(postgres_dsn: str) -> AsyncIterator[asyncpg.Pool]:
    pool = None
    for _ in range(30):
        with suppress(Exception):
            pool = await asyncpg.create_pool(
                postgres_dsn,
                ssl=False,
                min_size=1,
                max_size=5,
            )
            break
        await asyncio.sleep(1)

    if pool is None:
        raise RuntimeError(f'Could not connect to Postgres: {postgres_dsn}')

    async with pool.acquire() as conn:
        await conn.execute(SCHEMA_PATH.read_text())

    yield pool
    await pool.close()


@pytest.fixture(scope='session')
async def pg(raw_db_pool: asyncpg.Pool):
    async with raw_db_pool.acquire() as conn:
        yield conn


@pytest.fixture(autouse=True)
async def clean_db(raw_db_pool: asyncpg.Pool) -> AsyncIterator[None]:
    for _ in range(30):
        try:
            async with raw_db_pool.acquire() as conn:
                await conn.execute('TRUNCATE TABLE list_history, items, lists, users RESTART IDENTITY CASCADE')
            break
        except asyncpg.exceptions.PostgresError:
            await asyncio.sleep(1)
    else:
        raise RuntimeError('Could not clean test database')

    return
