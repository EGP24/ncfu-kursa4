from datetime import UTC, datetime
from decimal import Decimal

from entities.item import Item
from enums.item_sort_mode import ItemSortMode
from services import item_service


def test_build_item_edit_details_returns_none_when_no_changes() -> None:
    # Arrange
    old_item = _make_item(item_id=1, name='Milk', checked=False, position=0)
    new_item = _make_item(item_id=1, name='Milk', checked=False, position=0)

    # Act
    details = item_service._build_item_edit_details(old_item, new_item)

    # Assert
    assert details is None


def test_build_item_edit_details_collects_all_changed_fields() -> None:
    # Arrange
    old_item = _make_item(item_id=1, name='Milk', checked=False, position=0, quantity=Decimal('1.00'), unit='l')
    new_item = _make_item(item_id=1, name='Bread', checked=False, position=0, quantity=Decimal('2.50'), unit='pcs')

    # Act
    details = item_service._build_item_edit_details(old_item, new_item)

    # Assert
    assert details == 'название: «Milk» → «Bread»\nкол-во: 1.00 → 2.50\nед.: «l» → «pcs»'


def test_find_item_index_returns_none_when_item_missing() -> None:
    # Arrange
    items = [_make_item(item_id=1, name='A', checked=False, position=0)]

    # Act
    result = item_service._find_item_index(items, item_id=99)

    # Assert
    assert result is None


def test_move_item_reorders_list() -> None:
    # Arrange
    first = _make_item(item_id=1, name='A', checked=False, position=0)
    second = _make_item(item_id=2, name='B', checked=False, position=1)

    # Act
    moved = item_service._move_item([first, second], old_index=1, new_index=0)

    # Assert
    assert [item.id for item in moved] == [2, 1]


async def test_get_target_order_for_sort_manual_mode_uses_repository(monkeypatch) -> None:
    # Arrange
    manual_items = [_make_item(item_id=2, name='B', checked=False, position=1)]

    async def fake_get_items_by_list_id(db, *, list_id, use_manual_position=False):
        assert list_id == 42
        assert use_manual_position is True
        return manual_items

    monkeypatch.setattr(item_service.item_repo, 'get_items_by_list_id', fake_get_items_by_list_id)

    # Act
    result = await item_service._get_target_order_for_sort(
        db=object(),
        list_id=42,
        mode=ItemSortMode.manual,
        current_items=[_make_item(item_id=1, name='A', checked=False, position=0)],
    )

    # Assert
    assert result == manual_items


async def test_get_target_order_for_sort_unchecked_first_orders_by_checked_then_position() -> None:
    # Arrange
    items = [
        _make_item(item_id=1, name='A', checked=True, position=0),
        _make_item(item_id=2, name='B', checked=False, position=2),
        _make_item(item_id=3, name='C', checked=False, position=1),
    ]

    # Act
    result = await item_service._get_target_order_for_sort(
        db=object(),
        list_id=1,
        mode=ItemSortMode.unchecked_first,
        current_items=items,
    )

    # Assert
    assert [item.id for item in result] == [3, 2, 1]


async def test_get_target_order_for_sort_name_asc_orders_case_insensitive() -> None:
    # Arrange
    items = [
        _make_item(item_id=1, name='banana', checked=False, position=2),
        _make_item(item_id=2, name='Apple', checked=False, position=1),
        _make_item(item_id=3, name='apple', checked=False, position=0),
    ]

    # Act
    result = await item_service._get_target_order_for_sort(
        db=object(),
        list_id=1,
        mode=ItemSortMode.name_asc,
        current_items=items,
    )

    # Assert
    assert [item.id for item in result] == [3, 2, 1]


def _make_item(
    *,
    item_id: int,
    name: str,
    checked: bool,
    position: int,
    quantity: Decimal = Decimal('1.00'),
    unit: str | None = 'pcs',
) -> Item:
    now = datetime.now(tz=UTC)
    return Item(
        id=item_id,
        list_id=1,
        name=name,
        quantity=quantity,
        unit=unit,
        checked=checked,
        is_deleted=False,
        position=position,
        created_at=now,
        updated_at=now,
    )
