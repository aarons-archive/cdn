# Future
from __future__ import annotations

# Standard Library
import io
import os
import random
import string

# Packages
import aiohttp.web

# My stuff
from core.app import CDN
from utilities import exceptions, objects, snowflake, utils


async def post(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    utils.check_body_is_readable(request.can_read_body)
    utils.check_content_type(request.content_type, expected="multipart/form-data")

    reader = await request.multipart()

    if not (data := await reader.next()):
        raise exceptions.JSONResponseError("No multipart data received.", status=400)

    identifier = "".join(random.sample(string.ascii_lowercase, 20))
    format = data.filename.split(".").pop()

    buffer = io.FileIO(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../../../media/{identifier}.{format}")), mode="w")

    while True:
        if not (chunk := await data.read_chunk()):
            break
        buffer.write(chunk)

    buffer.close()

    data = await app.db.fetchrow(
        "INSERT INTO files (id, account_id, identifier, format, private) VALUES ($1, $2, $3, $4, $5) RETURNING *",
        snowflake.generate_snowflake(), authorised_account.id, identifier, format, False
    )

    file = objects.File(data)
    return aiohttp.web.json_response(file.info, status=201)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.post(r"/api/v1/files", post),
        ]
    )
