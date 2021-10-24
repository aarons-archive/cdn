# Future
from __future__ import annotations

# Packages
import aiohttp.web

# My stuff
from core.app import CDN
from utilities import exceptions


async def get(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    return aiohttp.web.json_response(account.info)


async def patch(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    # TODO: Account editing options here.
    return aiohttp.web.json_response(account.info)


async def delete(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    # TODO: Probably add some kind of additional check? idk
    await app.db.execute("DELETE FROM accounts WHERE id = $1", account.id)

    return aiohttp.web.json_response(status=204)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/v1/me", get),
            aiohttp.web.patch(r"/api/v1/me", patch),
            aiohttp.web.delete(r"/api/v1/me", delete),
        ]
    )
