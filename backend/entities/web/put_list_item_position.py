from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class PutListItemPositionRequest:
    position: int
    """Новая позиция элемента в списке (индекс с 0)"""
