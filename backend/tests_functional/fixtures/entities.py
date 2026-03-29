import jwt
import pytest

from tests_functional.helpers.factories import fc_get_list
from tests_functional.helpers.repositories import lists_repository, users_repository


@pytest.fixture
async def user(pg):
    return await users_repository.insert(pg)


@pytest.fixture
async def list_(pg, user):
    return await lists_repository.insert(pg, values=fc_get_list(owner_id=user['id']))


@pytest.fixture
async def user_token(user, jwt_secret):
    return jwt.encode({'user_id': user['id'], 'username': user['username']}, jwt_secret, algorithm='HS256')


@pytest.fixture
async def user_authorize_header(user_token):
    return {'Authorization': f'Bearer {user_token}'}
