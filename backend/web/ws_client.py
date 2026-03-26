from dataclasses import is_dataclass
from functools import lru_cache
from typing import Any, cast, overload

from aiohttp import WSMessage, web
from serpyco_rs import Serializer

from entities.web.ws import BaseWsMessage


@lru_cache(maxsize=256)
def _get_serializer[T: BaseWsMessage](tp: type[T]) -> Serializer[T]:
    return Serializer(tp)


@overload
def serialize_ws_value(value: None) -> None: ...


@overload
def serialize_ws_value(value: dict[str, Any]) -> dict[str, Any]: ...


@overload
def serialize_ws_value(value: BaseWsMessage) -> dict[str, Any]: ...


def serialize_ws_value(value: BaseWsMessage | dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if is_dataclass(value):
        return  _get_serializer(type(value)).dump(value)  # type: ignore[arg-type]

    return cast(dict[str, Any], value)


class WsClient:
    def __init__(self, raw_ws: web.WebSocketResponse) -> None:
        self._raw_ws = raw_ws

    @property
    def raw(self) -> web.WebSocketResponse:
        return self._raw_ws

    async def send_json(self, message: BaseWsMessage | dict[str, Any] | None) -> None:
        await self._raw_ws.send_json(serialize_ws_value(message))

    async def send_str(self, data: str) -> None:
        await self._raw_ws.send_str(data)

    async def send_bytes(self, data: bytes) -> None:
        await self._raw_ws.send_bytes(data)

    async def close(self) -> None:
        await self._raw_ws.close()

    def __aiter__(self) -> web.WebSocketResponse:
        return self._raw_ws.__aiter__()

    async def receive(self) -> WSMessage:
        return await self._raw_ws.receive()
