from decimal import Decimal

from database.simple import Database
from entities.item import InsertItem, Item
from entities.web.base import BaseItemResponse
from entities.web.ws import HistoryUpdatedMessage, ItemAddedMessage, ItemDeletedMessage, ItemUpdatedMessage
from enums.item_sort_mode import ItemSortMode
from enums.list_history_action import ListHistoryAction
from exceptions import ItemNotFound
from repositories import item_repo
from services import history_service, realtime_service
from services.get_or_raise import get_item_by_id_or_raise, update_item_or_raise
from services.permissions import check_access_for_list


async def create_item(
    *,
    db: Database,
    list_id: int,
    user_id: int | None,
    share_token: str | None,
    name: str,
    quantity: Decimal | None,
    unit: str | None,
    ws_clients: realtime_service.WsClients,
) -> Item:
    await check_access_for_list(db=db, list_id=list_id, user_id=user_id, share_token=share_token)

    inserted_item = await item_repo.insert_item(
        db,
        item=InsertItem(
            list_id=list_id,
            name=name,
            quantity=quantity or Decimal(1),
            unit=unit,
        ),
    )
    await history_service.append_log(
        db=db,
        list_id=list_id,
        action=ListHistoryAction.item_added,
        item_id=inserted_item.id,
        details=f'{inserted_item.quantity} {inserted_item.unit or ""}'.strip(),
        actor_id=user_id,
    )

    item_response = BaseItemResponse.from_entity(inserted_item)
    await realtime_service.broadcast(
        ws_clients=ws_clients,
        list_id=list_id,
        messages=[ItemAddedMessage(item=item_response), HistoryUpdatedMessage()],
    )
    return inserted_item


async def update_item(
    *,
    db: Database,
    list_id: int,
    item_id: int,
    user_id: int | None,
    share_token: str | None,
    name: str | None,
    quantity: Decimal | None,
    unit: str | None,
    checked: bool | None,
    ws_clients: realtime_service.WsClients,
) -> Item:
    await check_access_for_list(db=db, list_id=list_id, user_id=user_id, share_token=share_token)

    old_item = await get_item_by_id_or_raise(db, item_id=item_id, list_id=list_id)
    updated_item = await update_item_or_raise(
        db,
        item_id=old_item.id,
        list_id=old_item.list_id,
        name=name.strip() if name else None,
        quantity=quantity,
        unit=unit,
        checked=checked,
    )

    if old_item.checked != updated_item.checked:
        action = ListHistoryAction.item_checked if updated_item.checked else ListHistoryAction.item_unchecked
        await history_service.append_log(
            db=db,
            list_id=list_id,
            action=action,
            item_id=updated_item.id,
            details=None,
            actor_id=user_id,
        )
    else:
        details = _build_item_edit_details(old_item, updated_item)
        if details is not None:
            await history_service.append_log(
                db=db,
                list_id=list_id,
                action=ListHistoryAction.item_edited,
                item_id=updated_item.id,
                details=details,
                actor_id=user_id,
            )

    item_response = BaseItemResponse.from_entity(updated_item)
    await realtime_service.broadcast(
        ws_clients=ws_clients,
        list_id=list_id,
        messages=[ItemUpdatedMessage(item=item_response), HistoryUpdatedMessage()],
    )
    return updated_item


async def delete_item(
    *,
    db: Database,
    list_id: int,
    item_id: int,
    user_id: int | None,
    share_token: str | None,
    ws_clients: realtime_service.WsClients,
) -> None:
    await check_access_for_list(db=db, list_id=list_id, user_id=user_id, share_token=share_token)
    updated_item = await update_item_or_raise(db, item_id=item_id, list_id=list_id, is_deleted=True)

    await history_service.append_log(
        db=db,
        list_id=list_id,
        action=ListHistoryAction.item_deleted,
        item_id=updated_item.id,
        details=None,
        actor_id=user_id,
    )
    await realtime_service.broadcast(
        ws_clients=ws_clients,
        list_id=list_id,
        messages=[ItemDeletedMessage(item_id=item_id), HistoryUpdatedMessage()],
    )


async def move_item(
    *,
    db: Database,
    list_id: int,
    item_id: int,
    position: int,
    user_id: int | None,
    share_token: str | None,
    ws_clients: realtime_service.WsClients,
) -> Item:
    await check_access_for_list(db=db, list_id=list_id, user_id=user_id, share_token=share_token)

    items = await item_repo.get_items_by_list_id(db, list_id=list_id)
    old_index = _find_item_index(items, item_id=item_id)
    if old_index is None:
        raise ItemNotFound

    new_index = min(max(position, 0), len(items) - 1)
    if old_index == new_index:
        return items[old_index]

    reordered_items = _move_item(items, old_index=old_index, new_index=new_index)
    positions_by_id = {item.id: index for index, item in enumerate(reordered_items)}

    updated_items = await item_repo.update_items_positions(
        db,
        list_id=list_id,
        positions_by_id=positions_by_id,
        update_manual_positions=True,
    )
    updated_items_by_id = {item.id: item for item in updated_items}
    moved_item = updated_items_by_id.get(item_id)
    if moved_item is None:
        raise ItemNotFound

    await history_service.append_log(
        db=db,
        list_id=list_id,
        action=ListHistoryAction.item_edited,
        item_id=item_id,
        details=f'позиция: {old_index + 1} → {new_index + 1}',
        actor_id=user_id,
    )

    changed_items = [updated_items_by_id[item.id] for item in reordered_items if item.id in updated_items_by_id]
    await realtime_service.broadcast(
        ws_clients=ws_clients,
        list_id=list_id,
        messages=[
            *[ItemUpdatedMessage(item=BaseItemResponse.from_entity(item)) for item in changed_items],
            HistoryUpdatedMessage(),
        ],
    )
    return moved_item


async def sort_items(
    *,
    db: Database,
    list_id: int,
    mode: ItemSortMode,
    user_id: int | None,
    share_token: str | None,
    ws_clients: realtime_service.WsClients,
) -> list[Item]:
    await check_access_for_list(db=db, list_id=list_id, user_id=user_id, share_token=share_token)

    current_items = await item_repo.get_items_by_list_id(db, list_id=list_id)
    if not current_items:
        return []

    target_order = await _get_target_order_for_sort(
        db,
        list_id=list_id,
        mode=mode,
        current_items=current_items,
    )

    positions_by_id = {item.id: index for index, item in enumerate(target_order) if item.position != index}
    if not positions_by_id:
        return target_order

    updated_items = await item_repo.update_items_positions(
        db,
        list_id=list_id,
        positions_by_id=positions_by_id,
    )
    updated_items_by_id = {item.id: item for item in updated_items}
    sorted_items = [updated_items_by_id.get(item.id, item) for item in target_order]
    changed_items = [updated_items_by_id[item.id] for item in target_order if item.id in updated_items_by_id]

    await realtime_service.broadcast(
        ws_clients=ws_clients,
        list_id=list_id,
        messages=[ItemUpdatedMessage(item=BaseItemResponse.from_entity(item)) for item in changed_items],
    )
    return sorted_items


def _build_item_edit_details(old_item: Item, updated_item: Item) -> str | None:
    changes = []

    if old_item.name != updated_item.name:
        changes.append(f'название: «{old_item.name}» → «{updated_item.name}»')
    if old_item.quantity != updated_item.quantity:
        changes.append(f'кол-во: {old_item.quantity} → {updated_item.quantity}')
    if old_item.unit != updated_item.unit:
        changes.append(f'ед.: «{old_item.unit}» → «{updated_item.unit}»')

    if not changes:
        return None

    return '\n'.join(changes)


def _find_item_index(items: list[Item], *, item_id: int) -> int | None:
    for index, item in enumerate(items):
        if item.id == item_id:
            return index

    return None


def _move_item(items: list[Item], *, old_index: int, new_index: int) -> list[Item]:
    reordered_items = items.copy()
    moved_item = reordered_items.pop(old_index)
    reordered_items.insert(new_index, moved_item)
    return reordered_items


async def _get_target_order_for_sort(
    db: Database,
    *,
    list_id: int,
    mode: ItemSortMode,
    current_items: list[Item],
) -> list[Item]:
    if mode is ItemSortMode.manual:
        return await item_repo.get_items_by_list_id(db, list_id=list_id, use_manual_position=True)

    if mode is ItemSortMode.unchecked_first:
        return sorted(current_items, key=lambda item: (item.checked, item.position, item.id))

    if mode is ItemSortMode.name_asc:
        return sorted(current_items, key=lambda item: (item.name.casefold(), item.position, item.id))

    return current_items
