from enum import StrEnum


class ItemSortMode(StrEnum):
    manual = 'manual'
    """Ручной порядок элементов"""

    unchecked_first = 'unchecked_first'
    """Сначала неотмеченные"""

    name_asc = 'name_asc'
    """Сортировка по названию (А-Я)"""
