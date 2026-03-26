from dataclasses import dataclass
from datetime import datetime as datetime_

from entities.item import Item


@dataclass(slots=True, kw_only=True)
class InsertList:
    title: str
    """Название списка"""
    owner_id: int
    """ID владельца списка"""
    share_token: str | None = None
    """Токен для доступа к списку другими пользователями"""
    is_deleted: bool = False
    """Флаг, указывающий на удалённость списка"""


@dataclass(slots=True, kw_only=True)
class List(InsertList):
    id: int
    """ID списка"""
    created_at: datetime_
    """Дата и время создания списка"""
    updated_at: datetime_
    """Дата и время обновления списка"""


@dataclass(slots=True, kw_only=True)
class ListWithItems:
    list_: List
    """Данные списка"""
    items: list[Item]
    """Список ID объявлений, входящих в список"""
