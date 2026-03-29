from services import realtime_service


class _Message:
    def __init__(self, value: str) -> None:
        self.value = value


class _FakeWs:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[_Message] = []

    async def send_json(self, message) -> None:
        if self.fail:
            raise RuntimeError('socket closed')
        self.sent.append(message)


async def test_broadcast_sends_all_messages_to_all_clients() -> None:
    # Arrange
    first = _FakeWs()
    second = _FakeWs()
    messages = [_Message('a'), _Message('b')]
    ws_clients = {1: {first, second}}

    # Act
    await realtime_service.broadcast(ws_clients=ws_clients, list_id=1, messages=messages)

    # Assert
    assert [message.value for message in first.sent] == ['a', 'b']
    assert [message.value for message in second.sent] == ['a', 'b']


async def test_broadcast_removes_dead_clients() -> None:
    # Arrange
    alive = _FakeWs()
    dead = _FakeWs(fail=True)
    ws_clients = {1: {alive, dead}}

    # Act
    await realtime_service.broadcast(ws_clients=ws_clients, list_id=1, messages=[_Message('a')])

    # Assert
    assert ws_clients[1] == {alive}
