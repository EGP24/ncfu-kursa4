from typing import Any
from urllib.parse import unquote

import bcrypt
import jwt
from aiohttp import web

from config import JWT_SECRET
from entities.web.authorized_user import AuthorizedUser
from exceptions import AuthentificationRequired


AUTH_TOKEN_COOKIE_NAME = 'kursa4_auth_token'


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user_id: int, username: str) -> str:
    return jwt.encode({'user_id': user_id, 'username': username}, JWT_SECRET, algorithm='HS256')


def decode_token_to_json(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None


def decode_token_to_entity(token: str) -> AuthorizedUser | None:
    data = decode_token_to_json(token)
    if data is None or 'user_id' not in data or 'username' not in data:
        return None

    return AuthorizedUser(user_id=data['user_id'], username=data['username'])


def get_token_from_auth_header(request: web.Request) -> str | None:
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None

    token = auth[7:].strip()
    return token or None


def get_token_from_cookie(request: web.Request) -> str | None:
    token = request.cookies.get(AUTH_TOKEN_COOKIE_NAME, '').strip()
    if not token:
        return None

    return unquote(token)


async def get_user_from_request(request: web.Request) -> dict[str, Any] | None:
    header_token = get_token_from_auth_header(request)
    if header_token:
        payload = decode_token_to_json(header_token)
        if payload is not None:
            return payload

    cookie_token = get_token_from_cookie(request)
    if cookie_token:
        return decode_token_to_json(cookie_token)

    return None


async def require_auth(request: web.Request) -> dict[str, Any]:
    user = await get_user_from_request(request)
    if user is None:
        raise AuthentificationRequired
    return user
