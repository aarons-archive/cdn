# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web

# My stuff
from core.app import CDN


async def get(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response(
            {"error": "'Authorization' header was invalid or not found."},
            status=401
        )

    return aiohttp.web.json_response(account.info)


async def patch(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response(
            {"error": "'Authorization' header was invalid or not found."},
            status=401
        )

    raise NotImplementedError()


async def delete(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: CDN = request.app  # type: ignore

    if not (account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response(
            {"error": "'Authorization' header was invalid or not found."},
            status=401
        )

    await app.db.execute("DELETE FROM accounts WHERE id = $1", account.id)
    await app.db.execute("DELETE FROM files WHERE account_id = $1", account.id)

    return aiohttp.web.json_response(status=204)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/v1/me", get),  # type: ignore
            aiohttp.web.patch(r"/api/v1/me", patch),  # type: ignore
            aiohttp.web.delete(r"/api/v1/me", delete),  # type: ignore
        ]
    )
