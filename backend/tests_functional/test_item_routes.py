from decimal import Decimal

from .helpers.factories import fc_get_item
from .helpers.repositories import items_repository


async def test_post_list_items(app_client, pg, mocker, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']
    payload = {'name': 'Butter', 'quantity': '3.21', 'unit': 'pcs'}

    # Act
    response = await app_client.post(
        f'/api/lists/{list_id}/items',
        headers=user_authorize_header,
        json=payload,
    )

    # Assert
    response_data = await response.json()
    [item] = await items_repository.select(pg)
    assert item == {
        'id': mocker.ANY,
        'list_id': list_id,
        'name': payload['name'],
        'quantity': Decimal('3.21'),
        'unit': 'pcs',
        'checked': False,
        'position': 0,
        'manual_position': 0,
        'is_deleted': False,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
    }

    assert response_data == {
        'id': item['id'],
        'name': payload['name'],
        'quantity': payload['quantity'],
        'unit': payload['unit'],
        'checked': False,
        'position': 0,
    }


async def test_put_list_item_by_id(app_client, pg, mocker, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']
    item = await items_repository.insert(pg, values=fc_get_item(list_id=list_id))
    payload = {'name': 'Brown sugar', 'checked': True}

    # Act
    response = await app_client.put(
        f'/api/lists/{list_id}/items/{item["id"]}',
        headers=user_authorize_header,
        json=payload,
    )

    # Assert
    response_data = await response.json()
    [item] = await items_repository.select(pg)
    assert item == {
        'id': mocker.ANY,
        'list_id': list_id,
        'name': payload['name'],
        'quantity': mocker.ANY,
        'unit': mocker.ANY,
        'checked': payload['checked'],
        'position': mocker.ANY,
        'manual_position': mocker.ANY,
        'is_deleted': mocker.ANY,
        'created_at': mocker.ANY,
        'updated_at': mocker.ANY,
    }

    assert response_data == {
        'id': item['id'],
        'name': item['name'],
        'quantity': str(item['quantity']),
        'unit': item['unit'],
        'checked': payload['checked'],
        'position': 1,
    }


async def test_delete_list_item_by_id(app_client, pg, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']
    item = await items_repository.insert(pg, values=fc_get_item(list_id=list_id))

    # Act
    response = await app_client.delete(
        f'/api/lists/{list_id}/items/{item["id"]}',
        headers=user_authorize_header,
    )

    # Assert
    response_data = await response.json()
    [item] = await items_repository.select(pg)
    assert response_data == {'ok': True}
    assert item['is_deleted'] is True


async def test_put_list_item_position(app_client, pg, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']
    item1, item2 = await items_repository.insert(
        pg,
        values=[
            fc_get_item(list_id=list_id, position=1),
            fc_get_item(list_id=list_id, position=2),
        ],
    )

    # Act
    await app_client.put(
        f'/api/lists/{list_id}/items/{item2["id"]}/position',
        headers=user_authorize_header,
        json={'position': 0},
    )

    # Assert
    updated_item2, updated_item1 = await items_repository.select(pg, order_by=items_repository.table.c.position)
    assert updated_item2['id'] == item2['id']
    assert updated_item1['id'] == item1['id']


async def test_put_list_items_sort(app_client, pg, list_, user_authorize_header) -> None:
    # Arrange
    list_id = list_['id']
    item1, item2 = await items_repository.insert(
        pg,
        values=[
            fc_get_item(list_id=list_id, position=1, manual_position=1, checked=True),
            fc_get_item(list_id=list_id, position=2, manual_position=2, checked=False),
        ],
    )

    # Act
    response = await app_client.put(
        f'/api/lists/{list_id}/items/sort',
        headers=user_authorize_header,
        json={'mode': 'unchecked_first'},
    )

    # Assert
    response_data = await response.json()
    updated_item2, updated_item1 = await items_repository.select(pg, order_by=items_repository.table.c.position)
    assert updated_item2['id'] == item2['id']
    assert updated_item1['id'] == item1['id']

    assert updated_item2['manual_position'] == 2
    assert updated_item1['manual_position'] == 1

    assert updated_item2['position'] == 0
    assert updated_item1['position'] == 1

    assert response_data == [
        {
            'checked': False,
            'id': 2,
            'name': 'test',
            'position': 0,
            'quantity': '1.00',
            'unit': 'шт',
        },
        {
            'checked': True,
            'id': 1,
            'name': 'test',
            'position': 1,
            'quantity': '1.00',
            'unit': 'шт',
        },
    ]
