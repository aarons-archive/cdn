# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web

# My stuff
from core.app import CDN
from utilities import objects


async def get_all(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response({"error": "'Authorization' header was invalid or not found."}, status=401)

    files = await app.db.fetch("SELECT * FROM files WHERE account_id = $1", account.id)
    return aiohttp.web.json_response({"files": {file.identifier: file.info for file in [objects.File(data) for data in files]}})


async def get_one(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response({"error": "'Authorization' header was invalid or not found."}, status=401)

    identifier = request.match_info["identifier"]

    if not (data := await app.db.fetchrow("SELECT * FROM files WHERE account_id = $1 AND identifier = $2", account.id, identifier)):
        return aiohttp.web.json_response({"error": f"file with identifier '{identifier}' was not found."}, status=404)

    return aiohttp.web.json_response(objects.File(data).info)


async def delete(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response({"error": "'Authorization' header was invalid or not found."}, status=401)

    identifier = request.match_info["identifier"]

    if not await app.db.fetchrow("SELECT * FROM files WHERE account_id = $1 AND identifier = $2", account.id, identifier):
        return aiohttp.web.json_response({"error": f"file with identifier '{identifier}' was not found."}, status=404)

    await app.db.execute("DELETE FROM files WHERE account_id = $1 and identifier = $2", account.id, identifier)
    return aiohttp.web.json_response(status=204)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/v1/me/files", get_all),  # type: ignore
            aiohttp.web.get(r"/api/v1/me/files/{identifier:\w+}", get_one),  # type: ignore
            aiohttp.web.delete(r"/api/v1/me/files/{identifier:\w+}", delete),  # type: ignore
        ]
    )
