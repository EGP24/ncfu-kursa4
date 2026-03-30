import asyncio
from contextlib import suppress

import aiohttp_cors
from aiohttp import web

from app_keys import DB_KEY, WS_CLIENTS_KEY
from config import DATABASE_URL, HOST, PORT
from database.simple import Database
from routes.item_routes import routes as item_routes
from routes.list_routes import routes as list_routes
from routes.user_routes import routes as user_routes
from routes.ws_routes import routes as ws_routes


async def on_startup(app: web.Application) -> None:
    if (db := await Database(dsn=DATABASE_URL)) is None:
        raise RuntimeError('Failed to initialize database pool')

    app[DB_KEY] = db
    app[WS_CLIENTS_KEY] = {}


async def on_cleanup(app: web.Application) -> None:
    ws_clients = app.get(WS_CLIENTS_KEY, {})
    tasks = [ws.close() for clients in ws_clients.values() for ws in clients]

    if db := app.get(DB_KEY):
        tasks.append(db.close())

    await asyncio.gather(*tasks)


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_routes(user_routes)
    app.router.add_routes(list_routes)
    app.router.add_routes(item_routes)
    app.router.add_routes(ws_routes)

    cors = aiohttp_cors.setup(
        app,
        defaults={
            '*': aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                allow_methods='*',
            )
        },
    )
    for route in list(app.router.routes()):
        with suppress(ValueError):
            cors.add(route)

    return app


if __name__ == '__main__':
    application = create_app()
    web.run_app(application, host=HOST, port=PORT)
