from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from serpyco_rs.metadata import MinLength


@dataclass(slots=True, kw_only=True)
class PostListItemsRequest:
    name: Annotated[str, MinLength(1)]
    """Название элемента списка"""
    quantity: Decimal | None = None
    """Количество"""
    unit: Annotated[str | None, MinLength(1)] = None
    """Единица измерения"""
