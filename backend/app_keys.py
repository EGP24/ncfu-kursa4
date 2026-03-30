from aiohttp import web

from database.simple import Database
from web.ws_client import WsClient


DB_KEY = web.AppKey('db', Database)
WS_CLIENTS_KEY = web.AppKey('ws_client', dict[int, set[WsClient]])
