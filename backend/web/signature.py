import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import (
    Any,
    Protocol,
    get_type_hints,
)

from serpyco_rs import Serializer

from enums.handler_data_source import HandlerDataSource
from enums.handler_mode import HandlerMode
from enums.handler_user_kind import HandlerUserKind
from web.introspection import (
    _build_response_serializer,
    _extract_source_annotation,
    _extract_token_cookie_annotation,
    _extract_user_annotation,
    _is_request_type,
    _is_ws_client_type,
    _is_ws_type,
)


HandlerFunc = Callable[..., Awaitable[Any]]


class DataclassInstance(Protocol):
    __dataclass_fields__: dict[str, Any]

    def __hash__(self) -> int: ...


@dataclass
class HandlerSpec:
    func: HandlerFunc
    mode: HandlerMode

    request_param_name: str | None
    ws_param_name: str | None
    ws_client_param_name: str | None
    ws_clients_param_name: str | None
    db_param_name: str | None

    path_param_name: str | None
    path_param_type: type[DataclassInstance] | None

    query_param_name: str | None
    query_param_type: type[DataclassInstance] | None

    body_param_name: str | None
    body_param_type: type[DataclassInstance] | None

    optional_user_param_name: str | None
    optional_user_param_type: type[DataclassInstance] | None

    required_user_param_name: str | None
    required_user_param_type: type[DataclassInstance] | None

    cookie_token_param_name: str | None

    response_serializer: Serializer[type[DataclassInstance]] | None


def _analyze_handler_signature(func: HandlerFunc, *, mode: HandlerMode) -> HandlerSpec:
    sig = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)

    request_param_name: str | None = None
    ws_param_name: str | None = None
    ws_client_param_name: str | None = None
    ws_clients_param_name: str | None = None
    db_param_name: str | None = None

    path_param_name: str | None = None
    path_param_type: type[DataclassInstance] | None = None

    query_param_name: str | None = None
    query_param_type: type[DataclassInstance] | None = None

    body_param_name: str | None = None
    body_param_type: type[DataclassInstance] | None = None

    optional_user_param_name: str | None = None
    optional_user_param_type: type[DataclassInstance] | None = None

    required_user_param_name: str | None = None
    required_user_param_type: type[DataclassInstance] | None = None

    cookie_token_param_name: str | None = None

    unresolved_params: list[str] = []

    for name, param in sig.parameters.items():
        anno = hints.get(name, param.annotation)

        if _is_request_type(anno) or name == 'raw_request':
            if request_param_name is not None:
                raise TypeError(f'{func.__name__}: only one request/raw_request argument is supported')
            request_param_name = name
            continue

        if _is_ws_type(anno):
            if mode is not HandlerMode.ws:
                raise TypeError(f'{func.__name__}: web.WebSocketResponse can only be used with @ws_handler')
            if ws_param_name is not None:
                raise TypeError(f'{func.__name__}: only one web.WebSocketResponse argument is supported')
            ws_param_name = name
            continue

        if _is_ws_client_type(anno):
            if mode is not HandlerMode.ws:
                raise TypeError(f'{func.__name__}: WsClient can only be used with @ws_handler')
            if ws_client_param_name is not None:
                raise TypeError(f'{func.__name__}: only one WsClient argument is supported')
            ws_client_param_name = name
            continue

        if name == 'db':
            if db_param_name is not None:
                raise TypeError(f'{func.__name__}: only one db argument is supported')
            db_param_name = name
            continue

        if name == 'ws_clients':
            if ws_clients_param_name is not None:
                raise TypeError(f'{func.__name__}: only one ws_clients argument is supported')
            ws_clients_param_name = name
            continue

        source_info = _extract_source_annotation(anno)
        if source_info is not None:
            source, model_type = source_info

            if source is HandlerDataSource.path:
                if path_param_name is not None:
                    raise TypeError(f'{func.__name__}: only one FromPath argument is supported')
                path_param_name = name
                path_param_type = model_type
                continue

            if source is HandlerDataSource.query:
                if query_param_name is not None:
                    raise TypeError(f'{func.__name__}: only one FromQuery argument is supported')
                query_param_name = name
                query_param_type = model_type
                continue

            if source is HandlerDataSource.body:
                if mode is not HandlerMode.http:
                    raise TypeError(f'{func.__name__}: FromBody is not supported in @ws_handler')
                if body_param_name is not None:
                    raise TypeError(f'{func.__name__}: only one FromBody argument is supported')
                body_param_name = name
                body_param_type = model_type
                continue

        user_info = _extract_user_annotation(anno)
        if user_info is not None:
            user_kind, user_type = user_info

            if user_kind is HandlerUserKind.user_optional:
                if optional_user_param_name is not None:
                    raise TypeError(f'{func.__name__}: only one FromUser argument is supported')
                optional_user_param_name = name
                optional_user_param_type = user_type
                continue

            if user_kind is HandlerUserKind.user_required:
                if required_user_param_name is not None:
                    raise TypeError(f'{func.__name__}: only one FromRequiredUser argument is supported')
                required_user_param_name = name
                required_user_param_type = user_type
                continue

        if _extract_token_cookie_annotation(anno):
            if cookie_token_param_name is not None:
                raise TypeError(f'{func.__name__}: only one TokenCookie argument is supported')
            cookie_token_param_name = name
            continue

        unresolved_params.append(f'{name}: {anno!r}')

    if unresolved_params:
        raise TypeError(f'{func.__name__}: unsupported handler parameters: {", ".join(unresolved_params)}')

    return_type = hints.get('return', sig.return_annotation)
    response_serializer = None if mode is HandlerMode.ws else _build_response_serializer(return_type)

    return HandlerSpec(
        func=func,
        mode=mode,
        request_param_name=request_param_name,
        ws_param_name=ws_param_name,
        ws_client_param_name=ws_client_param_name,
        ws_clients_param_name=ws_clients_param_name,
        db_param_name=db_param_name,
        path_param_name=path_param_name,
        path_param_type=path_param_type,
        query_param_name=query_param_name,
        query_param_type=query_param_type,
        body_param_name=body_param_name,
        body_param_type=body_param_type,
        optional_user_param_name=optional_user_param_name,
        optional_user_param_type=optional_user_param_type,
        required_user_param_name=required_user_param_name,
        required_user_param_type=required_user_param_type,
        cookie_token_param_name=cookie_token_param_name,
        response_serializer=response_serializer,
    )
