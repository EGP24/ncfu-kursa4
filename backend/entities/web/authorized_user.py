from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class AuthorizedUser:
    user_id: int
    """Идентификатор пользователя"""
    username: str
    """Имя пользователя"""
