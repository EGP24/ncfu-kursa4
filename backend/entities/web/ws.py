from dataclasses import dataclass

from entities.web.base import BaseItemResponse
from enums.ws_message_type import WsMessageType


@dataclass(slots=True, kw_only=True)
class BaseWsMessage:
    type: WsMessageType
    """Тип сообщения"""


@dataclass(slots=True, kw_only=True)
class PongMessage(BaseWsMessage):
    type: WsMessageType = WsMessageType.pong
    """Ответ на ping от клиента, для поддержания соединения"""


@dataclass(slots=True, kw_only=True)
class HistoryUpdatedMessage(BaseWsMessage):
    type: WsMessageType = WsMessageType.history_updated
    """Сообщение о том, что список был обновлен, и клиенту нужно перезагрузить его историю"""


@dataclass(slots=True, kw_only=True)
class ItemAddedMessage(BaseWsMessage):
    type: WsMessageType = WsMessageType.item_added
    """Сообщение о том, что в списке появился новый элемент, и клиенту нужно его отобразить"""
    item: BaseItemResponse
    """Новый элемент, который нужно отобразить"""


@dataclass(slots=True, kw_only=True)
class ItemUpdatedMessage(BaseWsMessage):
    type: WsMessageType = WsMessageType.item_updated
    """Сообщение о том, что в списке появился новый элемент, и клиенту нужно его отобразить"""
    item: BaseItemResponse
    """Элемент, который нужно обновить в отображении"""


@dataclass(slots=True, kw_only=True)
class ItemDeletedMessage(BaseWsMessage):
    type: WsMessageType = WsMessageType.item_deleted
    """Сообщение о том, что из списка был удален элемент, и клиенту нужно удалить его из отображения"""
    item_id: int
    """ID элемента, который нужно удалить из отображения"""
