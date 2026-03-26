from dataclasses import dataclass

from entities.user import User


@dataclass(slots=True, kw_only=True)
class AuthResult:
    user: User
    """Авторизованный пользователь"""
    token: str
    """Токен для доступа к API"""
