from types import SimpleNamespace

import pytest
from aiohttp import web

import auth
from exceptions import AuthentificationRequired


def _request(*, headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None):
    return SimpleNamespace(headers=headers or {}, cookies=cookies or {})


def test_get_token_from_auth_header_returns_none_for_wrong_prefix() -> None:
    # Arrange
    request = _request(headers={'Authorization': 'Basic token'})

    # Act
    token = auth.get_token_from_auth_header(request)

    # Assert
    assert token is None


def test_get_token_from_auth_header_extracts_bearer_token() -> None:
    # Arrange
    request = _request(headers={'Authorization': 'Bearer  abc.def  '})

    # Act
    token = auth.get_token_from_auth_header(request)

    # Assert
    assert token == 'abc.def'


def test_get_token_from_cookie_unquotes_value() -> None:
    # Arrange
    request = _request(cookies={auth.AUTH_TOKEN_COOKIE_NAME: 'abc%2Edef'})

    # Act
    token = auth.get_token_from_cookie(request)

    # Assert
    assert token == 'abc.def'


async def test_get_user_from_request_prefers_valid_header_token(monkeypatch) -> None:
    # Arrange
    request = _request(
        headers={'Authorization': 'Bearer header-token'},
        cookies={auth.AUTH_TOKEN_COOKIE_NAME: 'cookie-token'},
    )

    def fake_decode(token: str):
        if token == 'header-token':
            return {'user_id': 1, 'username': 'header-user'}
        return {'user_id': 2, 'username': 'cookie-user'}

    monkeypatch.setattr(auth, 'decode_token_to_json', fake_decode)

    # Act
    payload = await auth.get_user_from_request(request)

    # Assert
    assert payload == {'user_id': 1, 'username': 'header-user'}


async def test_get_user_from_request_falls_back_to_cookie_when_header_invalid(monkeypatch) -> None:
    # Arrange
    request = _request(
        headers={'Authorization': 'Bearer header-token'},
        cookies={auth.AUTH_TOKEN_COOKIE_NAME: 'cookie-token'},
    )

    def fake_decode(token: str):
        if token == 'header-token':
            return None
        return {'user_id': 2, 'username': 'cookie-user'}

    monkeypatch.setattr(auth, 'decode_token_to_json', fake_decode)

    # Act
    payload = await auth.get_user_from_request(request)

    # Assert
    assert payload == {'user_id': 2, 'username': 'cookie-user'}


def test_decode_token_to_entity_returns_none_for_incomplete_payload(monkeypatch) -> None:
    # Arrange
    monkeypatch.setattr(auth, 'decode_token_to_json', lambda token: {'user_id': 1})

    # Act
    user = auth.decode_token_to_entity('bad-token')

    # Assert
    assert user is None


async def test_require_auth_raises_for_missing_user(monkeypatch) -> None:
    # Arrange
    request = _request()

    async def fake_get_user_from_request(req):
        return None

    monkeypatch.setattr(auth, 'get_user_from_request', fake_get_user_from_request)

    # Act
    with pytest.raises(web.HTTPUnauthorized) as exc:
        await auth.require_auth(request)

    # Assert
    assert exc.value.text == AuthentificationRequired.text
