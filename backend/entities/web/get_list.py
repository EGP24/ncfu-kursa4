from dataclasses import dataclass

from entities.item import Item
from entities.list import List
from entities.web.base import BaseItemResponse, BaseListResponse


@dataclass(slots=True, kw_only=True)
class GetListResponse(BaseListResponse):
    items: list[BaseItemResponse]
    """Список элементов"""

    @classmethod
    def from_entity(cls, list_: List, items: list[Item] | None = None) -> 'GetListResponse':
        items = items or []
        return cls(
            id=list_.id,
            title=list_.title,
            share_token=list_.share_token,
            created_at=list_.created_at,
            updated_at=list_.updated_at,
            items=[BaseItemResponse.from_entity(item) for item in items],
        )
