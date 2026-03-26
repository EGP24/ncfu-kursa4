from decimal import Decimal
from typing import Any

from sqlalchemy import case, func, literal, not_, select, update
from sqlalchemy.dialects.postgresql import insert

from database.simple import Database
from database.tables import items_table
from entities.item import InsertItem, Item
from mappers.item import insert_item_mapper, item_mapper
from utils.dt import now_utc
from utils.types import cast_optional


async def get_item_by_id(db: Database, *, item_id: int, list_id: int | None = None) -> Item | None:
    query = select(items_table).where(items_table.c.id == item_id, not_(items_table.c.is_deleted))
    if list_id:
        query = query.where(items_table.c.list_id == list_id)
    row = await db.fetchrow(query)
    return item_mapper.map_from(row) if row else None


async def get_items_by_list_id(
    db: Database,
    *,
    list_id: int,
    use_manual_position: bool = False,
) -> list[Item]:
    order_column = items_table.c.manual_position if use_manual_position else items_table.c.position

    query = (
        select(items_table)
        .where(items_table.c.list_id == list_id, not_(items_table.c.is_deleted))
        .order_by(order_column, items_table.c.id)
    )
    rows = await db.fetch(query)
    return item_mapper.maps_from(rows)


async def insert_item(db: Database, *, item: InsertItem) -> Item:
    now = now_utc()

    names = []
    values = []
    for name, value in insert_item_mapper.map_to(item).items():
        names.append(name)
        values.append(literal(value))

    query = (
        insert(items_table)
        .from_select(
            names + ['position', 'manual_position', 'created_at', 'updated_at'],
            select(
                *values,
                (func.coalesce(func.max(items_table.c.position), -1) + 1),
                (func.coalesce(func.max(items_table.c.position), -1) + 1),
                literal(now),
                literal(now),
            ).where(items_table.c.list_id == item.list_id),
        )
        .returning(items_table)
    )
    row = await db.fetchrow(query)
    return item_mapper.map_from(cast_optional(row))


async def update_item(
    db: Database,
    *,
    item_id: int,
    list_id: int | None = None,
    name: str | None = None,
    quantity: Decimal | None = None,
    unit: str | None = None,
    checked: bool | None = None,
    position: int | None = None,
    manual_position: int | None = None,
    is_deleted: bool | None = None,
) -> Item | None:
    values: dict[str, Any] = {'updated_at': now_utc()}
    query = update(items_table).where(items_table.c.id == item_id)
    if name is not None:
        values['name'] = name
    if quantity is not None:
        values['quantity'] = quantity
    if unit is not None:
        values['unit'] = unit
    if checked is not None:
        values['checked'] = checked
    if position is not None:
        values['position'] = position
    if manual_position is not None:
        values['manual_position'] = manual_position
    if is_deleted is not None:
        values['is_deleted'] = is_deleted
    if list_id is not None:
        query = query.where(items_table.c.list_id == list_id)

    query = query.values(**values).returning(items_table)
    row = await db.fetchrow(query)
    return item_mapper.map_from(row) if row else None


async def update_items_positions(
    db: Database,
    *,
    list_id: int,
    positions_by_id: dict[int, int],
    update_manual_positions: bool = False,
) -> list[Item]:
    if not positions_by_id:
        return []

    now = now_utc()
    whens = [(items_table.c.id == item_id, literal(position)) for item_id, position in positions_by_id.items()]

    query = (
        update(items_table)
        .where(
            items_table.c.list_id == list_id,
            items_table.c.id.in_(positions_by_id),
            not_(items_table.c.is_deleted),
        )
        .values(**_build_positions_values(whens=whens, now=now, update_manual_positions=update_manual_positions))
        .returning(items_table)
    )

    rows = await db.fetch(query)
    return item_mapper.maps_from(rows)


def _build_positions_values(
    *,
    whens: list[tuple[Any, Any]],
    now: Any,
    update_manual_positions: bool,
) -> dict[str, Any]:
    values: dict[str, Any] = {
        'position': case(*whens, else_=items_table.c.position),
        'updated_at': now,
    }

    if update_manual_positions:
        values['manual_position'] = case(*whens, else_=items_table.c.manual_position)

    return values
