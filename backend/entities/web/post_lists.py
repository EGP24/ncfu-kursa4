from dataclasses import dataclass
from typing import Annotated

from serpyco_rs.metadata import MinLength


@dataclass(slots=True, kw_only=True)
class PostListsRequest:
    title: Annotated[str, MinLength(1)]
    """Название списка"""
