from entities.web.ws import BaseWsMessage
from web.ws_client import WsClient


WsClients = dict[int, set[WsClient]]


async def broadcast(*, ws_clients: WsClients, list_id: int, messages: list[BaseWsMessage]) -> None:
    clients = ws_clients.get(list_id, set())
    dead = set()

    for ws in clients:
        for message in messages:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)

    clients -= dead
