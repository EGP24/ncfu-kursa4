from typing import Annotated

from aiohttp import web

from database.simple import Database
from entities.web.base import BaseItemResponse, StatusResponse
from entities.web.post_list_items import PostListItemsRequest
from entities.web.put_list_item import PutListItemRequest
from entities.web.put_list_item_position import PutListItemPositionRequest
from entities.web.put_list_items_sort import PutListItemsSortRequest
from services import item_service
from web import Body, ListItemPath, ListPath, ShareTokenQuery, User, WsClients, handler


routes = web.RouteTableDef()


@routes.post('/api/lists/{list_id}/items')
@handler
async def create_item(
    user_data: User,
    data: Annotated[PostListItemsRequest, Body()],
    query: ShareTokenQuery,
    path: ListPath,
    db: Database,
    ws_clients: WsClients,
) -> BaseItemResponse:
    inserted_item = await item_service.create_item(
        db=db,
        list_id=path.list_id,
        user_id=user_data.user_id if user_data else None,
        share_token=query.share_token,
        name=data.name,
        quantity=data.quantity,
        unit=data.unit,
        ws_clients=ws_clients,
    )
    return BaseItemResponse.from_entity(inserted_item)


@routes.put('/api/lists/{list_id}/items/{item_id:\\d+}')
@handler
async def update_item(
    user_data: User,
    data: Annotated[PutListItemRequest, Body()],
    query: ShareTokenQuery,
    path: ListItemPath,
    db: Database,
    ws_clients: WsClients,
) -> BaseItemResponse:
    updated_item = await item_service.update_item(
        db=db,
        list_id=path.list_id,
        item_id=path.item_id,
        user_id=user_data.user_id if user_data else None,
        share_token=query.share_token,
        name=data.name,
        quantity=data.quantity,
        unit=data.unit,
        checked=data.checked,
        ws_clients=ws_clients,
    )
    return BaseItemResponse.from_entity(updated_item)


@routes.delete('/api/lists/{list_id}/items/{item_id:\\d+}')
@handler
async def delete_item(
    user_data: User,
    query: ShareTokenQuery,
    path: ListItemPath,
    db: Database,
    ws_clients: WsClients,
) -> StatusResponse:
    await item_service.delete_item(
        db=db,
        list_id=path.list_id,
        item_id=path.item_id,
        user_id=user_data.user_id if user_data else None,
        share_token=query.share_token,
        ws_clients=ws_clients,
    )
    return StatusResponse()


@routes.put('/api/lists/{list_id}/items/{item_id:\\d+}/position')
@handler
async def move_item(
    user_data: User,
    data: Annotated[PutListItemPositionRequest, Body()],
    query: ShareTokenQuery,
    path: ListItemPath,
    db: Database,
    ws_clients: WsClients,
) -> BaseItemResponse:
    moved_item = await item_service.move_item(
        db=db,
        list_id=path.list_id,
        item_id=path.item_id,
        position=data.position,
        user_id=user_data.user_id if user_data else None,
        share_token=query.share_token,
        ws_clients=ws_clients,
    )
    return BaseItemResponse.from_entity(moved_item)


@routes.put('/api/lists/{list_id}/items/sort')
@handler
async def sort_items(
    user_data: User,
    data: Annotated[PutListItemsSortRequest, Body()],
    query: ShareTokenQuery,
    path: ListPath,
    db: Database,
    ws_clients: WsClients,
) -> list[BaseItemResponse]:
    sorted_items = await item_service.sort_items(
        db=db,
        list_id=path.list_id,
        mode=data.mode,
        user_id=user_data.user_id if user_data else None,
        share_token=query.share_token,
        ws_clients=ws_clients,
    )
    return [BaseItemResponse.from_entity(item) for item in sorted_items]
