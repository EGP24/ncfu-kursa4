async def test_get_ws_by_list_id(app_client, list_, user_token) -> None:
    # Arrange
    path = f'/api/ws/{list_["id"]}?token={user_token}'

    # Act
    ws = await app_client.ws_connect(path)
    await ws.send_str('ping')
    response_data = await ws.receive_json()

    # Assert
    assert response_data['type'] == 'pong'

    await ws.close()
