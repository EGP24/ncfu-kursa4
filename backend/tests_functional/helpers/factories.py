from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import bcrypt


def fc_get_item(
    list_id: int = 1,
    name: str = 'test',
    quantity: Decimal = Decimal(1),
    unit: str | None = 'шт',
    checked: bool = False,
    position: int = 1,
    manual_position: int = 1,
    is_deleted: bool = False,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> dict[str, Any]:
    now = datetime.now(tz=UTC)
    return {
        'list_id': list_id,
        'name': name,
        'quantity': quantity,
        'unit': unit,
        'checked': checked,
        'position': position,
        'manual_position': manual_position,
        'is_deleted': is_deleted,
        'created_at': created_at or now,
        'updated_at': updated_at or now,
    }


def fc_get_list(
    title: str = 'test',
    owner_id: int = 1,
    share_token: str | None = None,
    is_deleted: bool = False,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> dict[str, Any]:
    now = datetime.now(tz=UTC)
    return {
        'title': title,
        'owner_id': owner_id,
        'share_token': share_token,
        'is_deleted': is_deleted,
        'created_at': created_at or now,
        'updated_at': updated_at or now,
    }


def fc_get_user(
    username: str = 'test',
    password: str | None = 'test',
    password_hash: str | None = None,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    password_hash = password_hash or bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return {
        'username': username,
        'password_hash': password_hash,
        'created_at': created_at or datetime.now(tz=UTC),
    }


def fc_get_list_history(
    list_id: int = 1,
    action: str = 'item_added',
    item_id: int = 1,
    details: str | None = None,
    actor_id: int | None = None,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    now = datetime.now(tz=UTC)
    return {
        'list_id': list_id,
        'action': action,
        'item_id': item_id,
        'details': details,
        'actor_id': actor_id,
        'created_at': created_at or now,
    }
