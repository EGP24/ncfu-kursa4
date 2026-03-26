from enum import StrEnum


class ListHistoryAction(StrEnum):
    item_added = 'item_added'
    """Элемент добавлен в список"""
    item_deleted = 'item_deleted'
    """Элемент удален из списка"""
    item_edited = 'item_edited'
    """Элемент обновлен в списке"""
    item_checked = 'item_checked'
    """Элемент отмечен в списке"""
    item_unchecked = 'item_unchecked'
    """Элемент снят с отметки в списке"""
