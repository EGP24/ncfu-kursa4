from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from serpyco_rs.metadata import MinLength


@dataclass(slots=True, kw_only=True)
class PutListItemRequest:
    name: Annotated[str | None, MinLength(1)] = None
    """Название элемента списка"""
    quantity: Decimal | None = None
    """Цена элемента списка"""
    unit: Annotated[str | None, MinLength(1)] = None
    """Единица измерения элемента списка"""
    checked: bool | None = None
    """Статус элемента списка (отмечен/не отмечен)"""
