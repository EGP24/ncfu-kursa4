import json
from collections.abc import Awaitable, Callable
from typing import (
    Any,
)

from aiohttp import web
from multidict import MultiDict

from auth import get_token_from_cookie, get_user_from_request, require_auth
from web.introspection import _deserialize_user_value, _get_serializer
from web.signature import HandlerSpec
from web.ws_client import WsClient


HandlerFunc = Callable[..., Awaitable[Any]]


async def _resolve_common_kwargs(
    spec: HandlerSpec,
    request: web.Request,
    *,
    ws: web.WebSocketResponse | None = None,
    ws_client: WsClient | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}

    if spec.request_param_name is not None:
        kwargs[spec.request_param_name] = request

    if spec.ws_param_name is not None:
        if ws is None:
            raise RuntimeError('Internal error: websocket instance was not provided')
        kwargs[spec.ws_param_name] = ws

    if spec.ws_client_param_name is not None:
        if ws_client is None:
            raise RuntimeError('Internal error: WsClient instance was not provided')
        kwargs[spec.ws_client_param_name] = ws_client

    if spec.ws_clients_param_name is not None:
        kwargs[spec.ws_clients_param_name] = request.app.setdefault('ws_clients', {})

    if spec.db_param_name is not None:
        kwargs[spec.db_param_name] = request.app['db']

    if spec.optional_user_param_name is not None:
        raw_user = await get_user_from_request(request)
        kwargs[spec.optional_user_param_name] = _deserialize_user_value(
            raw_user,
            spec.optional_user_param_type,
        )

    if spec.required_user_param_name is not None:
        raw_user = await require_auth(request)
        kwargs[spec.required_user_param_name] = _deserialize_user_value(
            raw_user,
            spec.required_user_param_type,
        )

    if spec.cookie_token_param_name is not None:
        kwargs[spec.cookie_token_param_name] = get_token_from_cookie(request)

    if spec.path_param_name is not None:
        serializer = _get_serializer(spec.path_param_type)
        kwargs[spec.path_param_name] = serializer.load_query_params(MultiDict(request.match_info))

    if spec.query_param_name is not None:
        serializer = _get_serializer(spec.query_param_type)
        kwargs[spec.query_param_name] = serializer.load_query_params(request.query)

    if spec.body_param_name is not None:
        serializer = _get_serializer(spec.body_param_type)

        if request.method.upper() == 'GET':
            kwargs[spec.body_param_name] = serializer.load_query_params(request.query)
        else:
            try:
                raw_body = await request.json()
            except json.JSONDecodeError as exc:
                raise web.HTTPBadRequest(
                    text='{"error":"invalid_json"}',
                    content_type='application/json',
                ) from exc

            if not isinstance(raw_body, dict):
                raise web.HTTPBadRequest(
                    text='{"error":"json_body_must_be_object"}',
                    content_type='application/json',
                )

            kwargs[spec.body_param_name] = serializer.load(raw_body)

    return kwargs


def _resolve_http_response(spec: HandlerSpec, result: Any) -> web.StreamResponse:
    if isinstance(result, web.StreamResponse):
        return result

    if result is None:
        return web.Response(status=204)

    if spec.response_serializer is not None:
        return web.json_response(spec.response_serializer.dump(result))

    return web.json_response(result)
