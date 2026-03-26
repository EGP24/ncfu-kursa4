from aiohttp import web


ItemNotFound = web.HTTPNotFound(text='Item not found')
ListNotFound = web.HTTPNotFound(text='List not found')

InvalidCredentials = web.HTTPUnauthorized(text='Invalid credentials')
AuthentificationRequired = web.HTTPUnauthorized(text='Authentification required')

UserNameTaken = web.HTTPConflict(text='Username already taken')

AccessDenied = web.HTTPForbidden(text='Access denied')
