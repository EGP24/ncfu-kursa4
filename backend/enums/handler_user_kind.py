from enum import StrEnum


class HandlerUserKind(StrEnum):
    user_optional = 'user_optional'
    """Не обязательная авторизация"""
    user_required = 'user_required'
    """Обязательная авторизация"""
