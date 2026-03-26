from typing import Annotated

from aiohttp import web

from database.simple import Database
from entities.list_history import ListHistoryExtended
from entities.web.base import BaseListResponse, StatusResponse
from entities.web.get_list import GetListResponse
from entities.web.get_list_history import HistoryQuery
from entities.web.post_list_share import PostListShareResponse
from entities.web.post_lists import PostListsRequest
from entities.web.put_list import PutListRequest
from services import history_service, list_service
from web import Body, ListPath, Query, RequiredUser, ShareTokenPath, User, handler


routes = web.RouteTableDef()


@routes.get('/api/lists')
@handler
async def get_lists(user: RequiredUser, db: Database) -> list[BaseListResponse]:
    lists = await list_service.get_user_lists(db=db, user_id=user.user_id)
    return [BaseListResponse.from_entity(list_) for list_ in lists]


@routes.post('/api/lists')
@handler
async def create_list(user: RequiredUser, data: Annotated[PostListsRequest, Body()], db: Database) -> BaseListResponse:
    inserted_list = await list_service.create_list(db=db, user_id=user.user_id, title=data.title)
    return BaseListResponse.from_entity(inserted_list)


@routes.get('/api/lists/{list_id}')
@handler
async def get_list(user: RequiredUser, path: ListPath, db: Database) -> GetListResponse:
    result = await list_service.get_owned_list_with_items(db=db, user_id=user.user_id, list_id=path.list_id)
    return GetListResponse.from_entity(result.list_, result.items)


@routes.put('/api/lists/{list_id}')
@handler
async def update_list(
    user: RequiredUser,
    path: ListPath,
    data: Annotated[PutListRequest, Body()],
    db: Database,
) -> BaseListResponse:
    updated_list = await list_service.update_list_title(
        db=db,
        user_id=user.user_id,
        list_id=path.list_id,
        title=data.title,
    )
    return BaseListResponse.from_entity(updated_list)


@routes.delete('/api/lists/{list_id}')
@handler
async def delete_list(user: RequiredUser, path: ListPath, db: Database) -> StatusResponse:
    await list_service.delete_list(db=db, user_id=user.user_id, list_id=path.list_id)
    return StatusResponse()


@routes.post('/api/lists/{list_id}/share')
@handler
async def share_list(user: RequiredUser, path: ListPath, db: Database) -> PostListShareResponse:
    token = await list_service.share_list(db=db, user_id=user.user_id, list_id=path.list_id)
    return PostListShareResponse.from_token(token)


@routes.delete('/api/lists/{list_id}/share')
@handler
async def unshare_list(user: RequiredUser, path: ListPath, db: Database) -> StatusResponse:
    await list_service.unshare_list(db=db, user_id=user.user_id, list_id=path.list_id)
    return StatusResponse()


@routes.get('/api/shared/{share_token}')
@handler
async def get_shared_list(path: ShareTokenPath, db: Database) -> GetListResponse:
    result = await list_service.get_shared_list_with_items(db=db, share_token=path.share_token)
    return GetListResponse.from_entity(result.list_, result.items)


@routes.get('/api/lists/{list_id}/history')
@handler
async def get_list_history(
    user: User,
    path: ListPath,
    query: Annotated[HistoryQuery, Query()],
    db: Database,
) -> list[ListHistoryExtended]:
    return await history_service.get_list_history(
        db=db,
        list_id=path.list_id,
        user_id=user.user_id if user else None,
        share_token=query.share_token,
        actions=query.actions,
    )
