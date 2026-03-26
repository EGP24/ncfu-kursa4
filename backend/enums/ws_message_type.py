from enum import StrEnum


class WsMessageType(StrEnum):
    pong = 'pong'
    """Ответ на ping от клиента"""
    history_updated = 'history_updated'
    """Сообщение о том, что история списка была обновлена"""
    item_added = 'item_added'
    """Сообщение о том, что новый элемент был добавлен в список"""
    item_updated = 'item_updated'
    """Сообщение о том, что элемент был обновлен в списке"""
    item_deleted = 'item_deleted'
    """Сообщение о том, что элемент был удален из списка"""
