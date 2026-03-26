from dataclasses import dataclass
from typing import Annotated

from serpyco_rs.metadata import MinLength

from entities.user import User


@dataclass(slots=True, kw_only=True)
class PostRegisterUser:
    id: int
    """Идентификатор пользователя"""
    username: str
    """Имя пользователя"""

    @classmethod
    def from_entity(cls, user: User) -> 'PostRegisterUser':
        return cls(id=user.id, username=user.username)


@dataclass(slots=True, kw_only=True)
class PostRegisterRequest:
    username: str
    """Имя пользователя"""
    password: Annotated[str, MinLength(6)]
    """Пароль пользователя"""


@dataclass(slots=True, kw_only=True)
class PostRegisterResponse:
    token: str
    """JWT токен для аутентификации в последующих запросах"""
    user: PostRegisterUser
    """Информация о пользователе, который вошёл в систему"""

    @classmethod
    def from_entity(cls, user: User, token: str) -> 'PostRegisterResponse':
        return cls(token=token, user=PostRegisterUser.from_entity(user))
