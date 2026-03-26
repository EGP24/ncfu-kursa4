import aiohttp
from aiohttp import web

from auth import decode_token_to_entity
from database.simple import Database
from entities.web.ws import PongMessage
from exceptions import AccessDenied
from services.permissions import check_access_for_list
from web import AuthTokenCookie, ListPath, TokenAndShareTokenQuery, WsClients, ws_handler
from web.ws_client import WsClient


routes = web.RouteTableDef()


@routes.get('/api/ws/{list_id}')
@ws_handler
async def websocket_handler(
    ws: WsClient,
    path: ListPath,
    query: TokenAndShareTokenQuery,
    token_cookie: AuthTokenCookie,
    db: Database,
    ws_clients: WsClients,
) -> None:
    auth_token = query.token or token_cookie
    user = decode_token_to_entity(auth_token) if auth_token else None

    await check_access_for_list(
        db=db,
        list_id=path.list_id,
        user_id=user.user_id if user else None,
        share_token=query.share_token,
        side_effect=AccessDenied,
    )

    ws_clients.setdefault(path.list_id, set()).add(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT and msg.data == 'ping':
                await ws.send_json(PongMessage())
            elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
                break
    finally:
        ws_clients[path.list_id].discard(ws)
