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
import typing

# Packages
import aiohttp.web
import aiohttp_jinja2


class Pages:

    @aiohttp_jinja2.template('index.html')
    async def get_home(self, request: aiohttp.web.Request) -> typing.Optional[dict]:

        token = request.cookies.get('token')
        if token is None:
            return None

        account = await request.app.get_account_by_token(token=token)
        return account.info

    @aiohttp_jinja2.template('media.html')
    async def get_media(self, request: aiohttp.web.Request) -> typing.Union[aiohttp.web.HTTPFound, typing.Optional[dict]]:

        token = request.cookies.get('token')
        if token is None:
            return aiohttp.web.HTTPFound('/home')

        account = await request.app.get_account(token=token)

        files = await request.app.get_account_files(account_id=account.id)
        if not files:
            return None

        return {'images': [file.info for file in files], **account.info}

    @aiohttp_jinja2.template('account.html')
    async def get_account(self, request: aiohttp.web.Request) -> typing.Union[aiohttp.web.HTTPFound, typing.Optional[dict]]:

        token = request.cookies.get('token')
        if token is None:
            return aiohttp.web.HTTPFound('/home')

        account = await request.app.get_account(token=token)
        return account.info

    async def get_github(self, request: aiohttp.web.Request) -> aiohttp.web.HTTPFound:
        return aiohttp.web.HTTPFound('https://github.com/Axelancerr/AxelWeb')


def setup(app: aiohttp.web.Application):
    pages = Pages()

    app.add_routes([
        aiohttp.web.get(r'/home', pages.get_home),
        aiohttp.web.get(r'/home/media', pages.get_media),
        aiohttp.web.get(r'/home/account', pages.get_account),
        aiohttp.web.get(r'/home/github', pages.get_github),
    ])
