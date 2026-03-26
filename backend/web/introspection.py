import inspect
from dataclasses import is_dataclass
from functools import lru_cache
from typing import (
    Annotated,
    Any,
    get_args,
    get_origin,
)

from aiohttp import web
from serpyco_rs import SchemaValidationError, Serializer

from enums.handler_data_source import HandlerDataSource
from enums.handler_user_kind import HandlerUserKind
from web.marked_types import Body, Path, Query, RequiredUser, TokenCookie, User
from web.ws_client import WsClient


def _is_optional(tp: Any) -> bool:
    origin = get_origin(tp)
    return origin is not None and type(None) in get_args(tp)


def _strip_optional(tp: Any) -> Any:
    if not _is_optional(tp):
        return tp
    args = [arg for arg in get_args(tp) if arg is not type(None)]
    return args[0] if len(args) == 1 else tp


def _is_dataclass_type(tp: Any) -> bool:
    tp = _strip_optional(tp)
    return isinstance(tp, type) and is_dataclass(tp)


def _is_request_type(tp: Any) -> bool:
    return _strip_optional(tp) is web.Request


def _is_ws_type(tp: Any) -> bool:
    return _strip_optional(tp) is web.WebSocketResponse


def _is_ws_client_type(tp: Any) -> bool:
    return _strip_optional(tp) is WsClient


def _extract_source_annotation(tp: Any) -> tuple[HandlerDataSource, Any] | None:
    tp = _strip_optional(tp)
    origin = get_origin(tp)
    if origin is not Annotated:
        return None

    args = get_args(tp)
    if not args:
        return None

    base_type = _strip_optional(args[0])
    metadata = args[1:]

    found_source: HandlerDataSource | None = None
    for meta in metadata:
        if isinstance(meta, Body):
            if found_source is not None:
                raise TypeError('Only one source marker is allowed in Annotated[...]')
            found_source = HandlerDataSource.body
        elif isinstance(meta, Path):
            if found_source is not None:
                raise TypeError('Only one source marker is allowed in Annotated[...]')
            found_source = HandlerDataSource.path
        elif isinstance(meta, Query):
            if found_source is not None:
                raise TypeError('Only one source marker is allowed in Annotated[...]')
            found_source = HandlerDataSource.query

    if found_source is None:
        return None

    if not _is_dataclass_type(base_type):
        raise TypeError(f'Annotated source must wrap a dataclass type, got {base_type!r}')

    return found_source, base_type


def _extract_user_annotation(tp: Any) -> tuple[HandlerUserKind, Any] | None:
    tp = _strip_optional(tp)
    origin = get_origin(tp)
    if origin is not Annotated:
        return None

    args = get_args(tp)
    if not args:
        return None

    base_type = _strip_optional(args[0])
    metadata = args[1:]

    found: HandlerUserKind | None = None
    for meta in metadata:
        if isinstance(meta, User):
            if found is not None:
                raise TypeError('Only one auth marker is allowed in Annotated[...]')
            found = HandlerUserKind.user_optional
        elif isinstance(meta, RequiredUser):
            if found is not None:
                raise TypeError('Only one auth marker is allowed in Annotated[...]')
            found = HandlerUserKind.user_required

    if found is None:
        return None

    return found, base_type


def _extract_token_cookie_annotation(tp: Any) -> bool:
    tp = _strip_optional(tp)
    origin = get_origin(tp)
    if origin is not Annotated:
        return False

    args = get_args(tp)
    if not args:
        return False

    base_type = _strip_optional(args[0])
    metadata = args[1:]

    if base_type is not str:
        raise TypeError(f'TokenCookie marker expects str | None, got {base_type!r}')

    return any(isinstance(meta, TokenCookie) for meta in metadata)


@lru_cache(maxsize=256)
def _get_serializer[T: Any](tp: T) -> Serializer[T]:
    return Serializer(tp)


def _build_response_serializer[T: Any](tp: T) -> Serializer[T] | None:
    if tp is inspect.Signature.empty:
        return None
    try:
        return _get_serializer(_strip_optional(tp))
    except Exception:
        return None


def _deserialize_user_value(raw_user: Any, expected_type: Any) -> Any:
    if raw_user is None:
        return None

    expected_type = _strip_optional(expected_type)

    if expected_type is Any:
        return raw_user

    if expected_type is dict or get_origin(expected_type) is dict:
        return raw_user

    if _is_dataclass_type(expected_type):
        serializer = _get_serializer(expected_type)
        if not isinstance(raw_user, dict):
            raise TypeError(f'User value must be dict to deserialize into {expected_type!r}, got {type(raw_user)!r}')
        return serializer.load(raw_user)

    return raw_user


def _validation_error_response(exc: SchemaValidationError) -> web.Response:
    return web.json_response(
        {
            'error': 'validation_error',
            'details': [
                {
                    'message': err.message,
                    'instance_path': err.instance_path,
                }
                for err in exc.errors
            ],
        },
        status=400,
    )
