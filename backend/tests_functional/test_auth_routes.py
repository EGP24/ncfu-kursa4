from .helpers.factories import fc_get_user
from .helpers.repositories import users_repository


async def test_post_auth_register(app_client, pg, mocker) -> None:
    # Arrange
    payload = {'username': 'new-user', 'password': 'secret123'}

    # Act
    response = await app_client.post('/api/auth/register', json=payload)

    # Assert
    response_data = await response.json()
    [user] = await users_repository.select(pg)
    assert user == {
        'id': user['id'],
        'username': payload['username'],
        'password_hash': mocker.ANY,
        'created_at': mocker.ANY,
    }
    assert response_data == {
        'user': {'id': user['id'], 'username': payload['username']},
        'token': mocker.ANY,
    }


async def test_post_auth_login(app_client, pg, mocker) -> None:
    # Arrange
    password = 'owner-pass'
    user = await users_repository.insert(pg, values=fc_get_user(username='owner', password=password))

    # Act
    response = await app_client.post('/api/auth/login', json={'username': user['username'], 'password': password})

    # Assert
    response_data = await response.json()
    assert response_data == {
        'user': {'id': user['id'], 'username': user['username']},
        'token': mocker.ANY,
    }
