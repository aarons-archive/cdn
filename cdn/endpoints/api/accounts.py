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

# Packages
import aiohttp.web
import asyncpg

# My stuff
from utilities import enums, objects, snowflake


async def api_accounts_get(request: aiohttp.web.Request):

    if not (authorised_account := request.app.get_account_by_token(request.headers.get('Authorization'))):
        return aiohttp.web.json_response({'error': f'\'Authorization\' header was invalid or not found.'}, status=401)

    if not (account := request.app.get_account_by_id(int(request.match_info['id']))):
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' not found.'}, status=404)

    data = account.info if authorised_account.type.value >= enums.AccountType.OWNER.value else account.partial_info
    return aiohttp.web.json_response(data)


async def api_accounts_delete(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if not (authorised_account := request.app.get_account_by_token(request.headers.get('Authorization'))):
        return aiohttp.web.json_response({'error': f'\'Authorization\' header was invalid or not found.'}, status=401)

    if not (account := request.app.get_account_by_id(int(request.match_info['id']))):
        return aiohttp.web.json_response({'error': f'Account with id \'{request.match_info["id"]}\' not found.'}, status=404)

    if authorised_account.id != account.id and authorised_account.type.value >= enums.AccountType.ADMIN.value:
        return aiohttp.web.json_response({'error': f'Missing permissions to delete account with id \'{account.id}\'.'}, status=403)

    await account.delete()
    return aiohttp.web.Response(status=204)


async def api_accounts_post(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if not (authorised_account := request.app.get_account_by_token(request.headers.get('Authorization'))):
        return aiohttp.web.json_response({'error': f'\'Authorization\' header was invalid or not found.'}, status=401)

    if not authorised_account.type.value >= enums.AccountType.OWNER.value:
        return aiohttp.web.json_response({'error': f'You do not have permission to create accounts.'}, status=403)

    if not request.can_read_body:
        return aiohttp.web.json_response({'error': f'Request body must not be empty.'}, status=400)
    if request.content_type != 'application/json':
        return aiohttp.web.json_response({'error': f'An \'application/json\' Content-Type was expected, got \'{request.content_type}\''}, status=400)

    body = await request.json()

    if not (username := body.get('username')):
        return aiohttp.web.json_response({'error': f'Request body must have the \'username\' field.'}, status=400)
    if not (email := body.get('email')):
        return aiohttp.web.json_response({'error': f'Request body must have the \'email\' field.'}, status=400)
    if not (password := body.get('password')):
        return aiohttp.web.json_response({'error': f'Request body must have the \'password\' field.'}, status=400)

    token = f'{"bot" if bot is True else "user"}.{username}.{account_id}.{binascii.hexlify(os.urandom(32)).decode("utf-8")}'

    try:
        data = await request.app.db.fetchrow(
                'INSERT INTO accounts (id, username, token, bot, email, password, type) VALUES ($1, $2, $3, $4, $5, $6, crypt($7, gen_salt($8))) RETURNING *',
                snowflake.generate_snowflake(1, 1), username, token, body.get('bot', False), email, password, 'bf', body.get('type', 0)
        )
    except asyncpg.UniqueViolationError:
        return aiohttp.web.json_response({'error': f'The email \'{email}\' is already in use.'}, status=400)

    account = objects.Account(app=request.app, data=data)
    return aiohttp.web.json_response(account.info, status=201)


async def api_accounts_list_get(request: aiohttp.web.Request) -> aiohttp.web.Response:
    pass


async def api_accounts_stats_get(request: aiohttp.web.Request) -> aiohttp.web.Response:
    pass


async def api_accounts_purge_post(request: aiohttp.web.Request) -> aiohttp.web.Response:
    pass


def setup(app: aiohttp.web.Application) -> None:

    app.add_routes([
        aiohttp.web.get(r'/api/accounts/{id:\d+}', api_accounts_get),
        aiohttp.web.delete(r'/api/accounts/{id:\d+}', api_accounts_delete),

        aiohttp.web.post(r'/api/accounts', api_accounts_post),

        aiohttp.web.get(r'/api/accounts/{id:\d+}/list', api_accounts_list_get),
        aiohttp.web.get(r'/api/accounts/{id:\d+}/stats', api_accounts_stats_get),
        aiohttp.web.post(r'/api/accounts/{id:\d+}/purge', api_accounts_purge_post),
    ])
