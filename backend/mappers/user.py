from entities.user import InsertUser, User
from mappers import EntityMapper, ValueMapper


insert_user_mapper = EntityMapper(
    InsertUser,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)

user_mapper = EntityMapper(
    User,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)
