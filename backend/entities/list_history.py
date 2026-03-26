from dataclasses import dataclass
from datetime import datetime as datetime_

from enums.list_history_action import ListHistoryAction


@dataclass(slots=True, kw_only=True)
class InsertListHistory:
    list_id: int
    """Идентификатор списка"""
    action: ListHistoryAction
    """Действие, которое произошло со списком"""
    item_id: int
    """Идентификатор элемента"""
    details: str | None
    """Дополнительные сведения о действии"""
    actor_id: int | None
    """Идентификатор пользователя, который совершил действие"""


@dataclass(slots=True, kw_only=True)
class ListHistory(InsertListHistory):
    id: int
    """Идентификатор записи в истории"""
    created_at: datetime_
    """Дата и время создания записи в истории"""


@dataclass(slots=True, kw_only=True)
class ListHistoryExtended:
    id: int
    """Идентификатор записи в истории"""
    action: ListHistoryAction
    """Действие, которое произошло со списком"""
    item_name: str
    """Название элемента"""
    details: str | None
    """Дополнительные сведения о действии"""
    username: str
    """Имя пользователя, который совершил действие"""
    created_at: datetime_
    """Дата и время создания записи в истории"""
