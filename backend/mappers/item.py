from entities.item import InsertItem, Item
from mappers import EntityMapper, ValueMapper


insert_item_mapper = EntityMapper(
    InsertItem,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
    decimal_mapper=ValueMapper(),
)

item_mapper = EntityMapper(
    Item,
    without_camelcase=True,
    datetime_mapper=ValueMapper(),
    decimal_mapper=ValueMapper(),
)
