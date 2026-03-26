from sqlalchemy import case, select
from sqlalchemy.dialects.postgresql import insert

from database.simple import Database
from database.tables import items_table, list_history_table, users_table
from entities.list_history import InsertListHistory, ListHistory, ListHistoryExtended
from enums.list_history_action import ListHistoryAction
from mappers.list_history import insert_list_history_mapper, list_history_extended_mapper, list_history_mapper
from utils.dt import now_utc
from utils.types import cast_optional


async def get_list_history_extended_logs(
    db: Database,
    *,
    list_id: int,
    actions: list[ListHistoryAction] | None = None,
) -> list[ListHistoryExtended]:
    query = (
        select(
            list_history_table.c.id,
            list_history_table.c.action,
            items_table.c.name.label('item_name'),
            list_history_table.c.details,
            list_history_table.c.created_at,
            case((users_table.c.username.isnot(None), users_table.c.username), else_='Гость').label('username'),
        )
        .join(items_table, list_history_table.c.item_id == items_table.c.id)
        .outerjoin(users_table, users_table.c.id == list_history_table.c.actor_id)
        .where(items_table.c.list_id == list_id)
        .order_by(list_history_table.c.created_at.desc())
        .limit(100)
    )

    if actions:
        query = query.where(list_history_table.c.action.in_(actions))

    rows = await db.fetch(query)
    return list_history_extended_mapper.maps_from(rows)


async def insert_list_history_log(db: Database, *, log: InsertListHistory) -> ListHistory:
    query = (
        insert(list_history_table)
        .values(**insert_list_history_mapper.map_to(log), created_at=now_utc())
        .returning(list_history_table)
    )
    row = await db.fetchrow(query)
    return list_history_mapper.map_from(cast_optional(row))
