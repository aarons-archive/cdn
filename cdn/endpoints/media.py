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
import io
import os
import random

# Packages
import aiohttp.web
import asyncpg

# My stuff
from utilities import objects


class Media:

    async def get(self, request: aiohttp.web.Request) -> aiohttp.web.Response:

        authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
        if not authed_account:
            return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

        file = await request.app.get_file(identifier=request.match_info['identifier'])
        if not file:
            return aiohttp.web.json_response({'error': f'File with identifier \'{request.match_info["identifier"]}\' was not found.'}, status=404)

        if authed_account.id != file.id and authed_account.level not in {'admin', 'owner'}:
            return aiohttp.web.json_response({'error': f'You do not have permission to view file with identifier \'{file.identifier}\'.'}, status=403)

        return aiohttp.web.json_response(file.info, status=200)

    async def delete(self, request: aiohttp.web.Request) -> aiohttp.web.Response:

        authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
        if not authed_account:
            return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

        file = await request.app.get_file(identifier=request.match_info['identifier'])
        if not file:
            return aiohttp.web.json_response({'error': f'File with identifier \'{request.match_info["identifier"]}\' was not found.'}, status=404)

        if authed_account.id != file.account_id and authed_account.level not in {'admin', 'owner'}:
            return aiohttp.web.json_response({'error': f'You do not have permission to delete file with identifier \'{file.identifier}\'.'}, status=403)

        await request.app.db.execute('DELETE FROM files WHERE identifier = $1', file.identifier)
        os.remove(os.path.abspath(os.path.join(os.path.dirname(__file__),  f'../../../media/{file.filename}')))

        return aiohttp.web.json_response(status=204)

    async def post(self, request: aiohttp.web.Request) -> aiohttp.web.Response:

        authed_account = await request.app.get_account(token=request.headers.get("Authorization"))
        if not authed_account:
            return aiohttp.web.json_response({'error': f'\'Authorization\' was invalid or not found.'}, status=401)

        if request.content_type != 'multipart/form-data':
            return aiohttp.web.json_response({'error': f'A \'multipart/form-data\' Content-Type was expected.'}, status=400)

        reader = await request.multipart()
        data = await reader.next()

        if not data:
            return aiohttp.web.json_response({'error': f'No data was found.'}, status=400)

        file_name = ''.join(random.sample(request.app.words, 5))
        file_format = data.filename.split('.').pop()

        buffer = io.FileIO(os.path.abspath(os.path.join(os.path.dirname(__file__),  f'../../../media/{file_name}.{file_format}')), mode='w')

        while True:
            chunk = await data.read_chunk()
            if not chunk:
                break
            buffer.write(chunk)

        buffer.close()

        query = 'INSERT INTO files (account_id, identifier, format) VALUES ($1, $2, $3) RETURNING *'

        try:
            file_data = await request.app.db.fetchrow(query, authed_account.id, file_name, file_format)
        except asyncpg.UniqueViolationError:
            file_name = ''.join(random.sample(request.app.words, 3))
            file_data = await request.app.db.fetchrow(query, authed_account.id, file_name, file_format)

        file = objects.File(data=dict(file_data))
        return aiohttp.web.json_response(file.info, status=200)


def setup(app: aiohttp.web.Application) -> None:

    media = Media()

    app.add_routes([
        aiohttp.web.get(r'/api/media/{identifier:\w+}', media.get),
        aiohttp.web.delete(r'/api/media/{identifier:\w+}', media.delete),

        aiohttp.web.post(r'/api/media', media.post),
    ])
