from dataclasses import dataclass
from datetime import datetime as datetime_


@dataclass(slots=True, kw_only=True)
class InsertUser:
    username: str
    """Имя пользователя"""
    password_hash: str
    """Хэш пароля"""


@dataclass(slots=True, kw_only=True)
class User:
    id: int
    """Уникальный идентификатор пользователя"""
    username: str
    """Имя пользователя"""
    password_hash: str
    """Хэш пароля"""
    created_at: datetime_
    """Дата и время создания пользователя"""
