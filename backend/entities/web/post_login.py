from dataclasses import dataclass

from entities.user import User


@dataclass(slots=True, kw_only=True)
class PostLoginUser:
    id: int
    """Идентификатор пользователя"""
    username: str
    """Имя пользователя"""

    @classmethod
    def from_entity(cls, user: User) -> 'PostLoginUser':
        return cls(id=user.id, username=user.username)


@dataclass(slots=True, kw_only=True)
class PostLoginRequest:
    username: str
    """Имя пользователя"""
    password: str
    """Пароль пользователя"""


@dataclass(slots=True, kw_only=True)
class PostLoginResponse:
    token: str
    """JWT токен для аутентификации в последующих запросах"""
    user: PostLoginUser
    """Информация о пользователе, который вошёл в систему"""

    @classmethod
    def from_entity(cls, user: User, token: str) -> 'PostLoginResponse':
        return cls(token=token, user=PostLoginUser.from_entity(user))
