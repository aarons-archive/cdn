# Future
from __future__ import annotations

# Packages
import aiohttp.web

# My stuff
from core.app import CDN
from utilities import exceptions, objects


async def get_all(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    files = await app.db.fetch("SELECT * FROM files WHERE account_id = $1", authorised_account.id)
    return aiohttp.web.json_response({"files": {file.identifier: file.info for file in [objects.File(data) for data in files]}})


async def get_one(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    identifier = request.match_info["identifier"]

    if not (file := await app.get_file_owned_by(identifier, id=authorised_account.id)):
        return aiohttp.web.json_response({"error": f"you do not have a file with the identifier '{identifier}'."}, status=404)

    return aiohttp.web.json_response(file.info)


async def patch(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    identifier = request.match_info["identifier"]

    if not (file := await app.get_file_owned_by(identifier, id=authorised_account.id)):
        return aiohttp.web.json_response({"error": f"you do not have a file with the identifier '{identifier}'."}, status=404)

    # TODO: File editing options here.
    return aiohttp.web.json_response(file.info)


async def delete(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    identifier = request.match_info["identifier"]

    if not await app.get_file_owned_by(identifier, id=authorised_account.id):
        return aiohttp.web.json_response({"error": f"you do not have a file with the identifier '{identifier}'."}, status=404)

    # TODO: Probably add some kind of additional check? idk
    await app.db.execute("DELETE FROM files WHERE identifier = $1 AND account_id = $2", identifier, authorised_account.id)

    return aiohttp.web.json_response(status=204)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/v1/me/files", get_all),
            aiohttp.web.get(r"/api/v1/me/files/{identifier:\w+}", get_one),
            aiohttp.web.patch(r"/api/v1/me/files/{identifier:\w+}", patch),
            aiohttp.web.delete(r"/api/v1/me/files/{identifier:\w+}", delete),
        ]
    )
