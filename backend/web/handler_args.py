from typing import Annotated, TypeAlias

from entities.web.authorized_user import AuthorizedUser
from entities.web.base import (
    ListIdAndItemIdPath,
    ListIdPath,
    ShareTokenPath as ShareTokenPathEntity,
    ShareTokenQuery as ShareTokenQueryEntity,
    TokenAndShareTokenQuery as TokenAndShareTokenQueryEntity,
)
from .marked_types import (
    Path,
    Query,
    RequiredUser as FromRequiredUser,
    TokenCookie as FromTokenCookie,
    User as FromUser,
)
from .ws_client import WsClient


User: TypeAlias = Annotated[AuthorizedUser | None, FromUser()]
RequiredUser: TypeAlias = Annotated[AuthorizedUser, FromRequiredUser()]
AuthTokenCookie: TypeAlias = Annotated[str | None, FromTokenCookie()]

ListPath: TypeAlias = Annotated[ListIdPath, Path()]
ListItemPath: TypeAlias = Annotated[ListIdAndItemIdPath, Path()]

ShareTokenPath: TypeAlias = Annotated[ShareTokenPathEntity, Path()]
ShareTokenQuery: TypeAlias = Annotated[ShareTokenQueryEntity, Query()]
TokenAndShareTokenQuery: TypeAlias = Annotated[TokenAndShareTokenQueryEntity, Query()]

WsClients: TypeAlias = dict[int, set[WsClient]]
