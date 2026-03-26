from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class PostListShareResponse:
    share_token: str
    """Токен для доступа к списку"""

    @classmethod
    def from_token(cls, share_token: str) -> 'PostListShareResponse':
        return cls(share_token=share_token)
