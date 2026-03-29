from datetime import UTC, datetime

import pytest

from entities.list import List
from exceptions import ListNotFound
from services import get_or_raise, permissions


async def test_check_access_for_list_allows_owner(monkeypatch) -> None:
    # Arrange
    expected_list = _make_list(owner_id=7)

    async def fake_get_list_by_id(db, *, list_id):
        assert list_id == 1
        return expected_list

    monkeypatch.setattr(permissions.list_repo, 'get_list_by_id', fake_get_list_by_id)

    # Act
    result = await permissions.check_access_for_list(db=object(), list_id=1, user_id=7, share_token=None)

    # Assert
    assert result == expected_list


async def test_check_access_for_list_allows_share_token(monkeypatch) -> None:
    # Arrange
    expected_list = _make_list(owner_id=1, share_token='share-token')

    async def fake_get_list_by_id(db, *, list_id):
        return expected_list

    monkeypatch.setattr(permissions.list_repo, 'get_list_by_id', fake_get_list_by_id)

    # Act
    result = await permissions.check_access_for_list(
        db=object(),
        list_id=1,
        user_id=None,
        share_token='share-token',
    )

    # Assert
    assert result == expected_list


async def test_check_access_for_list_raises_side_effect_when_denied(monkeypatch) -> None:
    # Arrange
    expected_list = _make_list(owner_id=1, share_token='share-token')

    async def fake_get_list_by_id(db, *, list_id):
        return expected_list

    monkeypatch.setattr(permissions.list_repo, 'get_list_by_id', fake_get_list_by_id)

    # Act & Assert
    with pytest.raises(RuntimeError, match='denied'):
        await permissions.check_access_for_list(
            db=object(),
            list_id=1,
            user_id=999,
            share_token='wrong-token',
            side_effect=RuntimeError('denied'),
        )


async def test_check_access_for_list_raises_list_not_found_when_absent(monkeypatch) -> None:
    # Arrange
    async def fake_get_list_by_id(db, *, list_id):
        return None

    monkeypatch.setattr(permissions.list_repo, 'get_list_by_id', fake_get_list_by_id)

    # Act & Assert
    with pytest.raises(type(ListNotFound)):
        await permissions.check_access_for_list(db=object(), list_id=1, user_id=1, share_token=None)


async def test_raise_on_none_returns_value_for_non_none_result() -> None:
    # Arrange
    async def source(value: int) -> int | None:
        return value

    wrapped = get_or_raise.raise_on_none(RuntimeError('missing'))(source)

    # Act
    result = await wrapped(5)

    # Assert
    assert result == 5


async def test_raise_on_none_raises_for_none_result() -> None:
    # Arrange
    async def source() -> int | None:
        return None

    # Act
    wrapped = get_or_raise.raise_on_none(RuntimeError('missing'))(source)

    # Assert
    with pytest.raises(RuntimeError, match='missing'):
        await wrapped()


def _make_list(*, owner_id: int, share_token: str | None = None) -> List:
    now = datetime.now(tz=UTC)
    return List(
        id=1,
        title='test',
        owner_id=owner_id,
        share_token=share_token,
        is_deleted=False,
        created_at=now,
        updated_at=now,
    )
