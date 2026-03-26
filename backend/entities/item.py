from dataclasses import dataclass
from datetime import datetime as datetime_
from decimal import Decimal


@dataclass(slots=True, kw_only=True)
class InsertItem:
    list_id: int
    """Идентификатор списка"""
    name: str
    """Название карточки"""
    quantity: Decimal
    """Количество"""
    unit: str | None
    """Единица измерения"""
    checked: bool = False
    """Статус выполнения"""
    is_deleted: bool = False
    """Статус удаления"""


@dataclass(slots=True, kw_only=True)
class Item(InsertItem):
    id: int
    """Идентификатор карточки"""
    position: int
    """Позиция карточки в списке"""
    created_at: datetime_
    """Дата и время создания карточки"""
    updated_at: datetime_
    """Дата и время обновления карточки"""
