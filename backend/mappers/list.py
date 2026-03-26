from entities.list import InsertList, List
from mappers import EntityMapper, ValueMapper


insert_list_mapper = EntityMapper(
    InsertList,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)

list_mapper = EntityMapper(
    List,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)
