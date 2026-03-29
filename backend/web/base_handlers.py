from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from aiohttp import web
from serpyco_rs import SchemaValidationError

from enums.handler_mode import HandlerMode
from web.introspection import _validation_error_response
from web.resolvers import _resolve_common_kwargs, _resolve_http_response
from web.signature import _analyze_handler_signature
from web.ws_client import WsClient


HandlerFunc = Callable[..., Awaitable[Any]]


def handler(func: HandlerFunc) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
    spec = _analyze_handler_signature(func, mode=HandlerMode.http)

    @wraps(func)
    async def wrapper(request: web.Request) -> web.StreamResponse:
        try:
            kwargs = await _resolve_common_kwargs(spec, request)
        except SchemaValidationError as exc:
            return _validation_error_response(exc)

        result = await spec.func(**kwargs)
        return _resolve_http_response(spec, result)

    return wrapper


def ws_handler(func: HandlerFunc) -> Callable[[web.Request], Awaitable[web.WebSocketResponse]]:
    spec = _analyze_handler_signature(func, mode=HandlerMode.ws)

    @wraps(func)
    async def wrapper(request: web.Request) -> web.WebSocketResponse:
        raw_ws = web.WebSocketResponse()
        await raw_ws.prepare(request)
        typed_ws = WsClient(raw_ws)

        try:
            kwargs = await _resolve_common_kwargs(spec, request, ws=raw_ws, ws_client=typed_ws)
        except SchemaValidationError as exc:
            await raw_ws.send_json(
                {
                    'type': 'error',
                    'error': 'validation_error',
                    'details': [
                        {
                            'message': err.message,
                            'instance_path': err.instance_path,
                        }
                        for err in exc.errors
                    ],
                }
            )
            await raw_ws.close()
            return raw_ws

        result = await spec.func(**kwargs)

        if result is None:
            return raw_ws

        if isinstance(result, web.WebSocketResponse):
            return result

        raise TypeError(
            f'{func.__name__}: websocket handler must return None or web.WebSocketResponse'
        )

    return wrapper
