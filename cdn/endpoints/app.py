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

# My stuff
from utilities import objects


class App:

    async def post_login(self, request: aiohttp.web.Request) -> aiohttp.web.Response:

        if not request.can_read_body:
            return aiohttp.web.json_response({'error': f'Request body must not be empty.'}, status=400)

        if request.content_type != 'application/x-www-form-urlencoded':
            return aiohttp.web.json_response({'error': f'An \'application/x-www-form-urlencoded\' Content-Type was expected.'}, status=400)

        data = await request.post()

        username = data.get('username')
        if not username:
            return aiohttp.web.json_response({'error': f'The \'username\' field is required.'}, status=400)
        password = data.get('password')
        if not password:
            return aiohttp.web.json_response({'error': f'The \'password\' field is required.'}, status=400)

        account_data = await request.app.db.fetchrow('SELECT * FROM accounts WHERE username = $1 and (password = crypt($2, password))', username, password)
        if not account_data:
            return aiohttp.web.json_response({'error': f'An account with that username and password combination was not found.'}, status=401)

        account = objects.Account(data=dict(account_data), app=request.app)

        response = aiohttp.web.HTTPFound('/home')
        response.set_cookie('token', account.token, max_age=1209600, samesite='Strict')

        return response

    async def post_logout(self, request: aiohttp.web.Request) -> aiohttp.web.Response:

        if request.cookies.get('token') is None:
            return aiohttp.web.json_response({'error': 'You are not logged in.'})

        response = aiohttp.web.HTTPFound('/home')
        response.del_cookie('token')

        return response


def setup(app: aiohttp.web.Application) -> None:

    app_endpoints = App()

    app.add_routes([
        aiohttp.web.post(r'/api/login', app_endpoints.post_login),
        aiohttp.web.post(r'/api/logout', app_endpoints.post_logout)
    ])
