#  cdn
#  Copyright (C) 2020 Axel#3456
#
#  cdn is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  cdn is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with cdn. If not, see https://www.gnu.org/licenses/.


# Future
from __future__ import annotations

# Standard Library
import binascii
import os

# Packages
import aiohttp.web
import asyncpg

# My stuff
from utilities import objects, snowflake


async def get(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: app.AxelWeb = request.app

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE id = $1', int(request.match_info['id']))
    if not account_data:
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' was not found.'})

    account = objects.Account(data=dict(account_data))
    data = account.info if authed_account.level in {'owner', 'admin'} else account.partial_info

    return aiohttp.web.json_response(data, status=200)

async def delete(request: aiohttp.web.Request) -> aiohttp.web.Response:

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE id = $1', int(request.match_info['id']))
    if not account_data:
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' was not found.'})

    account = objects.Account(data=dict(account_data))

    if authed_account.id != account.id and authed_account.level not in {'admin', 'owner'}:
        return aiohttp.web.json_response({'error': f'You do not have permission to delete account with id \'{account.id}\'.'}, status=403)

    files = await request.app.db.fetch('SELECT * FROM files WHERE account_id = $1', account.id)
    await request.app.db.execute('DELETE FROM accounts where id = $1', account.id)

    for file in files:
        file = objects.File(data=dict(file))
        try:
            os.remove(os.path.abspath(os.path.join(os.path.dirname(__file__), f'../../../media/{file.filename}')))
        except FileNotFoundError:
            continue

    return aiohttp.web.Response(status=204)

async def post( request: aiohttp.web.Request) -> aiohttp.web.Response:

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    if authed_account.level not in {'admin', 'owner'}:
        return aiohttp.web.json_response({'error': f'You do not have permission to create accounts.'}, status=403)

    if not request.can_read_body:
        return aiohttp.web.json_response({'error': f'Request body must not be empty.'}, status=400)

    if request.content_type != 'application/json':
        return aiohttp.web.json_response({'error': f'An \'application/json\' Content-Type was expected.'}, status=400)

    body = await request.json()

    username = body.get('username')
    if not username:
        return aiohttp.web.json_response({'error': f'Request body must have the \'username\' field.'}, status=400)
    email = body.get('email')
    if not email:
        return aiohttp.web.json_response({'error': f'Request body must have the \'email\' field.'}, status=400)
    password = body.get('password')
    if not password:
        return aiohttp.web.json_response({'error': f'Request body must have the \'password\' field.'}, status=400)

    account_id = snowflake.generate_snowflake(1, 1)
    level = body.get('level', 'user')
    bot = body.get('bot', False)
    token = f'{"bot" if bot is True else "user"}.{username}.{account_id}.{binascii.hexlify(os.urandom(32)).decode("utf-8")}'

    query = 'INSERT INTO accounts (id, username, token, level, bot, email, password) VALUES ($1, $2, $3, $4, $5, $6, crypt($7, gen_salt($8))) RETURNING *'

    try:
        account_data = await request.app.db.fetchrow(query, account_id, username, token, level, bot, email, password, 'bf')
    except asyncpg.UniqueViolationError:
        return aiohttp.web.json_response({'error': f'The email \'{email}\' is already in use.'}, status=400)

    account = objects.Account(data=dict(account_data))

    return aiohttp.web.json_response(account.info, status=201)

async def post_purge(request: aiohttp.web.Request) -> aiohttp.web.Response:

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE id = $1', int(request.match_info['id']))
    if not account_data:
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' was not found.'})

    account = objects.Account(data=dict(account_data))

    if authed_account.id != account.id and authed_account.level not in {'admin', 'owner'}:
        return aiohttp.web.json_response({'error': f'You do not have permission to purge the files of account with id \'{account.id}\'.'}, status=403)

    files = await request.app.db.fetch('SELECT * FROM files WHERE account_id = $1', account.id)
    await request.app.db.execute('DELETE FROM files WHERE account_id = $1', account.id)

    for file in files:
        file = objects.File(data=dict(file))
        try:
            os.remove(os.path.abspath(os.path.join(os.path.dirname(__file__), f'../../../media/{file.filename}')))
        except FileNotFoundError:
            continue

    return aiohttp.web.Response(status=204)

async def get_stats(request: aiohttp.web.Request) -> aiohttp.web.Response:

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE id = $1', int(request.match_info['id']))
    if not account_data:
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' was not found.'})

    account = objects.Account(data=dict(account_data))

    if authed_account.id != account.id and authed_account.level not in {'admin', 'owner'}:
        return aiohttp.web.json_response({'error': f'You do not have permission to view the stats of account with id \'{account.id}\'.'}, status=403)

    files = await request.app.get_account_files(account_id=account.id)

    file_data = {
        'last_upload': files[0].info if len(files) > 0 else None,
        'upload_count': len(files)
    }
    return aiohttp.web.json_response({**account.partial_info, **file_data}, status=200)

async def get_list(request: aiohttp.web.Request) -> aiohttp.web.Response:

    authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
    if not authed_account:
        return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

    account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE id = $1', int(request.match_info['id']))
    if not account_data:
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' was not found.'})

    account = objects.Account(data=dict(account_data))

    if authed_account.id != account.id and authed_account.level not in {'admin', 'owner'}:
        return aiohttp.web.json_response({'error': f'You do not have permission to view the files of account with id \'{account.id}\'.'}, status=403)

    files = await request.app.get_account_files(account_id=account.id)
    return aiohttp.web.json_response({file.identifier: file.info for file in files}, status=200)


def setup(app: aiohttp.web.Application) -> None:

    app.add_routes([
        aiohttp.web.get(r'/api/accounts/{id:\d+}', get),
        aiohttp.web.delete(r'/api/accounts/{id:\d+}', delete),

        aiohttp.web.post(r'/api/accounts', post),

        aiohttp.web.post(r'/api/accounts/{id:\d+}/purge', post_purge),
        aiohttp.web.get(r'/api/accounts/{id:\d+}/stats', get_stats),
        aiohttp.web.get(r'/api/accounts/{id:\d+}/list', get_list),
    ])
