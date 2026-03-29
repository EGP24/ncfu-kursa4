from collections.abc import Callable, Iterable, Sequence
from typing import Any, cast

from sqlalchemy import Column, Table, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGCompiler
from sqlalchemy.sql.dml import Insert as InsertObject, Update as UpdateObject
from sqlalchemy.sql.elements import ClauseElement, ColumnElement, UnaryExpression
from sqlalchemy.util import immutabledict

from .factories import fc_get_item, fc_get_list, fc_get_list_history, fc_get_user
from .tables import items_table, list_history_table, lists_table, users_table


DbRecord = dict[str, Any]


class PgRepository:
    _dialect: PGDialect_asyncpg = postgresql.asyncpg.dialect()  # type: ignore[no-untyped-call]

    def __init__(self, *, table: Table, default_factory: Callable[..., dict[str, Any]]) -> None:
        self.table = table
        self.default_factory = default_factory

    async def select(
        self,
        pg,
        *,
        where_clause: ColumnElement | None = None,
        columns: Iterable[Column] | None = None,
        order_by: Iterable[UnaryExpression] | None = None,
    ) -> list[DbRecord]:
        query = select(self.table)
        if columns is not None:
            query = select(*columns).select_from(self.table)
        if where_clause is not None:
            query = query.where(where_clause)
        if order_by is not None:
            query = query.order_by(order_by)
        sql, params = self.compile_query(query)
        return [dict(i) for i in await pg.fetch(sql, *params)]

    async def insert(
        self,
        pg,
        *,
        values: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> DbRecord | list[DbRecord]:
        if values is None:
            values = self.default_factory()
        query = insert(self.table).values(values).returning(self.table)
        sql, params = self.compile_query(query)
        rows = [dict(i) for i in await pg.fetch(sql, *params)]
        return rows if isinstance(values, list) and len(values) > 1 else rows[0]

    def _get_compiled_statement(self, statement: ClauseElement) -> PGCompiler:
        return cast(
            PGCompiler,
            statement.compile(
                dialect=self._dialect,
                compile_kwargs={
                    'render_postcompile': True,
                },
            ),
        )

    def compile_query(self, statement: ClauseElement) -> tuple[str, tuple[Any, ...]]:
        compiled: PGCompiler = self._get_compiled_statement(statement)

        positiontup: Sequence[str] | None = compiled.positiontup

        if not positiontup:
            return compiled.string, ()

        default_values = self._get_default_values(statement, compiled)

        values = {
            **compiled.params,
            **default_values,
        }

        params = tuple(values[param] for param in positiontup)

        return compiled.string, params

    def _get_default_values(self, statement: ClauseElement, compiled: PGCompiler) -> dict[str, Any]:
        if isinstance(statement, InsertObject):
            attr_name = 'default'
        elif isinstance(statement, UpdateObject):
            attr_name = 'onupdate'
        else:
            return {}

        _values = cast(immutabledict[str, Any], statement._values)
        statement_values: frozenset[str] = frozenset(_values.keys()) if _values else frozenset()

        params: dict[str, Any] = {}

        for col in statement.table.columns:
            if col.name in statement_values:
                continue

            attr = getattr(col, attr_name)

            if attr and compiled.params.get(col.name) is None:
                if attr.is_sequence:
                    params[col.name] = func.nextval(attr.name)
                elif attr.is_scalar:
                    params[col.name] = attr.arg
                elif attr.is_callable:
                    params[col.name] = attr.arg({})

        return params


items_repository = PgRepository(
    table=items_table,
    default_factory=fc_get_item,
)
lists_repository = PgRepository(
    table=lists_table,
    default_factory=fc_get_list,
)
users_repository = PgRepository(
    table=users_table,
    default_factory=fc_get_user,
)
list_history_repository = PgRepository(
    table=list_history_table,
    default_factory=fc_get_list_history,
)
