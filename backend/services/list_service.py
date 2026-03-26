import secrets

from database.simple import Database
from entities.list import InsertList, List, ListWithItems
from repositories import item_repo, list_repo
from services.get_or_raise import (
    delete_list_or_raise,
    get_list_by_id_or_raise,
    get_list_by_share_token_or_raise,
    set_list_share_token_or_raise,
    update_list_title_or_raise,
)


async def get_user_lists(*, db: Database, user_id: int) -> list[List]:
    return await list_repo.get_lists_by_owner_id(db, owner_id=user_id)


async def create_list(*, db: Database, user_id: int, title: str) -> List:
    return await list_repo.insert_list(db, list_=InsertList(title=title, owner_id=user_id))


async def get_owned_list_with_items(*, db: Database, user_id: int, list_id: int) -> ListWithItems:
    list_ = await get_list_by_id_or_raise(db, list_id=list_id, owner_id=user_id)
    items = await item_repo.get_items_by_list_id(db, list_id=list_id)
    return ListWithItems(list_=list_, items=items)


async def update_list_title(*, db: Database, user_id: int, list_id: int, title: str) -> List:
    return await update_list_title_or_raise(db, list_id=list_id, owner_id=user_id, new_name=title)


async def delete_list(*, db: Database, user_id: int, list_id: int) -> None:
    await delete_list_or_raise(db, list_id=list_id, owner_id=user_id)


async def share_list(*, db: Database, user_id: int, list_id: int) -> str:
    token = secrets.token_urlsafe(32)
    updated_list = await set_list_share_token_or_raise(
        db,
        list_id=list_id,
        owner_id=user_id,
        share_token=token,
    )
    return updated_list.share_token or token


async def unshare_list(*, db: Database, user_id: int, list_id: int) -> None:
    await set_list_share_token_or_raise(
        db,
        list_id=list_id,
        owner_id=user_id,
        share_token=None,
    )


async def get_shared_list_with_items(*, db: Database, share_token: str) -> ListWithItems:
    list_ = await get_list_by_share_token_or_raise(db, share_token=share_token)
    items = await item_repo.get_items_by_list_id(db, list_id=list_.id)
    return ListWithItems(list_=list_, items=items)
