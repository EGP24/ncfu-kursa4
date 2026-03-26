from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.simple import Database
from database.tables import users_table
from entities.user import InsertUser, User
from mappers.user import insert_user_mapper, user_mapper
from utils.dt import now_utc
from utils.types import cast_optional


async def get_user_by_username(db: Database, *, username: str) -> User | None:
    query = select(users_table).where(users_table.c.username == username)
    row = await db.fetchrow(query)
    return user_mapper.map_from(row) if row else None


async def insert_user(db: Database, *, user: InsertUser) -> User:
    query = insert(users_table).values(**insert_user_mapper.map_to(user), created_at=now_utc()).returning(users_table)
    row = await db.fetchrow(query)
    return user_mapper.map_from(cast_optional(row))
