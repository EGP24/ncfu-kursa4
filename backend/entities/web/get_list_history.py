from dataclasses import dataclass

from entities.web.base import ShareTokenQuery
from enums.list_history_action import ListHistoryAction


@dataclass(slots=True, kw_only=True)
class HistoryQuery(ShareTokenQuery):
    actions: list[ListHistoryAction] | None = None
    """Фильтры истории по типу действий"""
