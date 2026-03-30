import re
from collections.abc import Generator
from typing import Any

import asyncpg
from asyncpg import Pool, Record
from asyncpg.pool import PoolAcquireContext
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import ClauseElement


_SQLALCHEMY_BIND_RE = re.compile(r'%\(([^)]+)\)s')


class Database:
    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = 1,
        max_size: int = 10,
        command_timeout: float = 60.0,
    ) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._command_timeout = command_timeout
        self._pool: Pool | None = None

        self._dialect = postgresql.dialect()  # type: ignore[no-untyped-call]

    async def __ainit__(self) -> 'Database | None':
        if self._pool is not None:
            return None

        self._pool = await asyncpg.create_pool(
            dsn=self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
            command_timeout=self._command_timeout,
        )
        return self

    def __await__(self) -> Generator[Any, None, 'Database | None']:
        return self.__ainit__().__await__()

    @property
    def pool(self) -> Pool:
        if self._pool is None:
            raise RuntimeError('Database pool is not initialized')
        return self._pool

    async def close(self) -> None:
        if self._pool is None:
            return

        await self._pool.close()
        self._pool = None

    def acquire(self) -> PoolAcquireContext:
        return self.pool.acquire()

    def _compile(
        self,
        statement: ClauseElement,
    ) -> tuple[str, list[Any]]:
        compiled = statement.compile(
            dialect=self._dialect,
            compile_kwargs={'render_postcompile': True},
        )

        sql = str(compiled)
        params_dict = compiled.params

        args: list[Any] = []

        def replacer(match: re.Match[str]) -> str:
            param_name = match.group(1)
            args.append(params_dict[param_name])
            return f'${len(args)}'

        sql = _SQLALCHEMY_BIND_RE.sub(replacer, sql)
        return sql, args

    async def fetch(
        self,
        statement: ClauseElement,
    ) -> list[Record]:
        sql, args = self._compile(statement)
        async with self.acquire() as conn:
            return await conn.fetch(sql, *args)

    async def fetchrow(
        self,
        statement: ClauseElement,
    ) -> Record | None:
        sql, args = self._compile(statement)
        async with self.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def fetchval(
        self,
        statement: ClauseElement,
        *,
        column: int = 0,
    ) -> Any:
        sql, args = self._compile(statement)
        async with self.acquire() as conn:
            return await conn.fetchval(sql, *args, column=column)

    async def execute(
        self,
        statement: ClauseElement,
    ) -> str:
        sql, args = self._compile(statement)
        async with self.acquire() as conn:
            return await conn.execute(sql, *args)
