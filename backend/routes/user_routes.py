from typing import Annotated

from aiohttp import web

from database.simple import Database
from entities.web.post_login import PostLoginRequest, PostLoginResponse
from entities.web.post_register import PostRegisterRequest, PostRegisterResponse
from services import auth_service
from web import Body, handler


routes = web.RouteTableDef()


@routes.post('/api/auth/register')
@handler
async def register(data: Annotated[PostRegisterRequest, Body()], db: Database) -> PostRegisterResponse:
    result = await auth_service.register(db=db, username=data.username, password=data.password)
    return PostRegisterResponse.from_entity(user=result.user, token=result.token)


@routes.post('/api/auth/login')
@handler
async def login(data: Annotated[PostLoginRequest, Body()], db: Database) -> PostLoginResponse:
    result = await auth_service.login(db=db, username=data.username, password=data.password)
    return PostLoginResponse.from_entity(user=result.user, token=result.token)
