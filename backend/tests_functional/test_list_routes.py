from decimal import Decimal

from .helpers.factories import fc_get_item, fc_get_list, fc_get_list_history
from .helpers.repositories import items_repository, list_history_repository, lists_repository


async def test_get_lists(app_client, pg, mocker, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']

    # Act
    response = await app_client.get('/api/lists', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    assert response_data == [
        {
            'id': list_id,
            'title': 'test',
            'share_token': None,
            'created_at': mocker.ANY,
            'updated_at': mocker.ANY,
        }
    ]


async def test_post_lists(app_client, pg, mocker, user_authorize_header, user) -> None:
    # Arrange
    payload = {'title': 'Weekend groceries'}

    # Act
    response = await app_client.post('/api/lists', headers=user_authorize_header, json=payload)
    response_data = await response.json()

    # Assert
    [inserted_list] = await lists_repository.select(pg)
    assert inserted_list == {
        'id': inserted_list['id'],
        'title': payload['title'],
        'owner_id': user['id'],
        'share_token': None,
        'is_deleted': False,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
    }
    assert response_data == {
        'id': inserted_list['id'],
        'title': payload['title'],
        'share_token': None,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
    }


async def test_get_list_by_id(app_client, pg, list_, user_authorize_header, mocker) -> None:
    # Arrange
    list_id = list_['id']
    first_item, second_item = await items_repository.insert(
        pg,
        values=[
            fc_get_item(
                list_id=list_id, name='Milk', quantity=Decimal('2.00'), unit='l', position=0, manual_position=0
            ),
            fc_get_item(
                list_id=list_id, name='Bread', quantity=Decimal('1.00'), unit='pcs', position=1, manual_position=1
            ),
        ],
    )

    # Act
    response = await app_client.get(f'/api/lists/{list_id}', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    assert response_data == {
        'id': list_id,
        'title': list_['title'],
        'share_token': None,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
        'items': [
            {
                'id': first_item['id'],
                'name': 'Milk',
                'quantity': '2.00',
                'unit': 'l',
                'checked': False,
                'position': 0,
            },
            {
                'id': second_item['id'],
                'name': 'Bread',
                'quantity': '1.00',
                'unit': 'pcs',
                'checked': False,
                'position': 1,
            },
        ],
    }


async def test_put_list_by_id(app_client, pg, list_, user_authorize_header, mocker) -> None:
    # Arrange
    list_id = list_['id']
    payload = {'title': 'Updated groceries'}

    # Act
    response = await app_client.put(f'/api/lists/{list_id}', headers=user_authorize_header, json=payload)
    response_data = await response.json()

    # Assert
    [updated_list] = await lists_repository.select(pg)
    assert updated_list['title'] == payload['title']
    assert response_data == {
        'id': list_id,
        'title': payload['title'],
        'share_token': None,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
    }


async def test_delete_list_by_id(app_client, pg, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']

    # Act
    response = await app_client.delete(f'/api/lists/{list_id}', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    [deleted_list] = await lists_repository.select(pg)
    assert deleted_list['is_deleted'] is True
    assert response_data == {'ok': True}


async def test_post_list_share(app_client, pg, list_, user_authorize_header, mocker) -> None:
    # Arrange
    list_id = list_['id']

    # Act
    response = await app_client.post(f'/api/lists/{list_id}/share', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    [updated_list] = await lists_repository.select(pg)
    assert updated_list['share_token'] == response_data['share_token']
    assert response_data == {'share_token': mocker.ANY}


async def test_delete_list_share(app_client, pg, user, user_authorize_header) -> None:
    # Arrange
    list_ = await lists_repository.insert(pg, values=fc_get_list(owner_id=user['id'], share_token='share-token'))
    list_id = list_['id']

    # Act
    response = await app_client.delete(f'/api/lists/{list_id}/share', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    [updated_list] = await lists_repository.select(pg)
    assert updated_list['share_token'] is None
    assert response_data == {'ok': True}


async def test_get_shared_list(app_client, pg, user, mocker) -> None:
    # Arrange
    list_ = await lists_repository.insert(pg, values=fc_get_list(owner_id=user['id'], share_token='share-token'))
    first_item, second_item = await items_repository.insert(
        pg,
        values=[
            fc_get_item(
                list_id=list_['id'], name='Milk', quantity=Decimal('2.00'), unit='l', position=0, manual_position=0
            ),
            fc_get_item(
                list_id=list_['id'], name='Bread', quantity=Decimal('1.00'), unit='pcs', position=1, manual_position=1
            ),
        ],
    )

    # Act
    response = await app_client.get('/api/shared/share-token')
    response_data = await response.json()

    # Assert
    assert response_data == {
        'id': list_['id'],
        'title': list_['title'],
        'share_token': 'share-token',
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
        'items': [
            {
                'id': first_item['id'],
                'name': 'Milk',
                'quantity': '2.00',
                'unit': 'l',
                'checked': False,
                'position': 0,
            },
            {
                'id': second_item['id'],
                'name': 'Bread',
                'quantity': '1.00',
                'unit': 'pcs',
                'checked': False,
                'position': 1,
            },
        ],
    }


async def test_get_list_history(app_client, pg, user, user_authorize_header, mocker) -> None:
    # Arrange
    list_ = await lists_repository.insert(pg, values=fc_get_list(owner_id=user['id']))
    item = await items_repository.insert(pg, values=fc_get_item(list_id=list_['id'], name='Milk'))
    await list_history_repository.insert(
        pg,
        values=fc_get_list_history(
            list_id=list_['id'],
            action='item_added',
            item_id=item['id'],
            details='2 l',
            actor_id=user['id'],
        ),
    )

    # Act
    response = await app_client.get(f'/api/lists/{list_["id"]}/history', headers=user_authorize_header)
    response_data = await response.json()

    # Assert
    assert response_data == [
        {
            'id': mocker.ANY,
            'action': 'item_added',
            'item_name': 'Milk',
            'details': '2 l',
            'username': user['username'],
            'created_at': mocker.ANY,
        }
    ]
