from sqlalchemy import not_, select
from sqlalchemy.dialects.postgresql import insert

from database.simple import Database
from database.tables import lists_table
from entities.list import InsertList, List
from mappers.list import insert_list_mapper, list_mapper
from utils.dt import now_utc
from utils.types import cast_optional


async def get_list_by_id(db: Database, *, list_id: int, owner_id: int | None = None) -> List | None:
    query = select(lists_table).where(lists_table.c.id == list_id, not_(lists_table.c.is_deleted))
    if owner_id is not None:
        query = query.where(lists_table.c.owner_id == owner_id)
    row = await db.fetchrow(query)
    return list_mapper.map_from(row) if row else None


async def get_list_by_share_token(db: Database, *, share_token: str) -> List | None:
    query = select(lists_table).where(lists_table.c.share_token == share_token, not_(lists_table.c.is_deleted))
    row = await db.fetchrow(query)
    return list_mapper.map_from(row) if row else None


async def get_lists_by_owner_id(db: Database, *, owner_id: int) -> list[List]:
    query = select(lists_table).where(lists_table.c.owner_id == owner_id, not_(lists_table.c.is_deleted))
    rows = await db.fetch(query)
    return list_mapper.maps_from(rows)


async def insert_list(db: Database, *, list_: InsertList) -> List:
    now = now_utc()
    query = (
        insert(lists_table)
        .values(
            **insert_list_mapper.map_to(list_),
            created_at=now,
            updated_at=now,
        )
        .returning(lists_table)
    )
    row = await db.fetchrow(query)
    return list_mapper.map_from(cast_optional(row))


async def update_list_title(db: Database, *, list_id: int, owner_id: int | None = None, new_name: str) -> List | None:
    now = now_utc()
    query = (
        lists_table.update()
        .where(lists_table.c.id == list_id)
        .values(title=new_name, updated_at=now)
        .returning(lists_table)
    )
    if owner_id is not None:
        query = query.where(lists_table.c.owner_id == owner_id)
    row = await db.fetchrow(query)
    return list_mapper.map_from(row) if row else None


async def delete_list(db: Database, *, list_id: int, owner_id: int | None = None) -> List | None:
    now = now_utc()
    query = (
        lists_table.update()
        .where(lists_table.c.id == list_id)
        .values(is_deleted=True, updated_at=now)
        .returning(lists_table)
    )
    if owner_id is not None:
        query = query.where(lists_table.c.owner_id == owner_id)
    row = await db.fetchrow(query)
    return list_mapper.map_from(row) if row else None


async def set_share_token(
        db: Database,
        *,
        list_id: int,
        owner_id: int | None = None,
        share_token: str | None,
) -> List | None:
    now = now_utc()
    query = (
        lists_table.update()
        .where(lists_table.c.id == list_id)
        .values(share_token=share_token, updated_at=now)
        .returning(lists_table)
    )
    if owner_id is not None:
        query = query.where(lists_table.c.owner_id == owner_id)
    row = await db.fetchrow(query)
    return list_mapper.map_from(row) if row else None
