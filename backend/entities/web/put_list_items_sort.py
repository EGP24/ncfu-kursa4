from dataclasses import dataclass

from enums.item_sort_mode import ItemSortMode


@dataclass(slots=True, kw_only=True)
class PutListItemsSortRequest:
    mode: ItemSortMode
    """Режим автоматической сортировки элементов"""
