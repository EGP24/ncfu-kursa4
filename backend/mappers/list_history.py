from entities.list_history import InsertListHistory, ListHistory, ListHistoryExtended
from mappers import EntityMapper, ValueMapper


insert_list_history_mapper = EntityMapper(
    InsertListHistory,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)

list_history_mapper = EntityMapper(
    ListHistory,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)

list_history_extended_mapper = EntityMapper(
    ListHistoryExtended,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
)
