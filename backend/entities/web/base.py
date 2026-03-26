from dataclasses import dataclass
from datetime import datetime as datetime_
from decimal import Decimal

from entities.item import Item
from entities.list import List


@dataclass(slots=True, kw_only=True)
class ListIdPath:
    list_id: int
    """Идентификатор списка"""


@dataclass(slots=True, kw_only=True)
class ListIdAndItemIdPath(ListIdPath):
    item_id: int
    """Идентификатор элемента списка"""


@dataclass(slots=True, kw_only=True)
class ShareTokenPath:
    share_token: str
    """Токен доступа к списку"""


@dataclass(slots=True, kw_only=True)
class ShareTokenQuery:
    share_token: str | None = None
    """Токен доступа к списку"""


@dataclass(slots=True, kw_only=True)
class TokenAndShareTokenQuery(ShareTokenQuery):
    token: str | None = None
    """Токен доступа к API"""


@dataclass(slots=True, kw_only=True)
class StatusResponse:
    ok: bool = True
    """Результат операции"""


@dataclass(slots=True, kw_only=True)
class BaseListResponse:
    id: int
    """Идентификатор списка"""
    title: str
    """Название списка"""
    share_token: str | None
    """Токен для доступа к списку"""
    created_at: datetime_
    """Дата и время создания списка"""
    updated_at: datetime_
    """Дата и время обновления списка"""

    @classmethod
    def from_entity(cls, list_: List) -> 'BaseListResponse':
        return cls(
            id=list_.id,
            title=list_.title,
            share_token=list_.share_token,
            created_at=list_.created_at,
            updated_at=list_.updated_at,
        )


@dataclass(slots=True, kw_only=True)
class BaseItemResponse:
    id: int
    """Идентификатор элемента списка"""
    name: str
    """Название элемента списка"""
    quantity: Decimal
    """Количество"""
    unit: str | None
    """Единица измерения"""
    checked: bool
    """Статус элемента списка (отмечен/не отмечен)"""
    position: int
    """Позиция элемента в списке"""

    @classmethod
    def from_entity(cls, item: Item) -> 'BaseItemResponse':
        return cls(
            id=item.id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            checked=item.checked,
            position=item.position,
        )
