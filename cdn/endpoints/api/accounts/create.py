# Future
from __future__ import annotations

# Standard Library
import binascii
import os
from typing import Any

# Packages
import aiohttp
import aiohttp.web
import asyncpg.exceptions

# My stuff
from core.app import CDN
from utilities import enums, exceptions, objects, snowflake, utils


async def create_account(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    if not request.can_read_body:
        return aiohttp.web.json_response(
            {"error": "request body must not be empty."},
            status=400
        )
    if request.content_type != "application/application/json":
        return aiohttp.web.json_response(
            {"error": f"expected content-type 'application/json', received '{request.content_type}'"},
            status=400
        )

    app: CDN = request.app  # type: ignore

    if not (authorised_account := await app.fetch_account_by_token(request.headers.get("Authorization"))):
        return aiohttp.web.json_response(
            {"error": "'Authorization' header was invalid or not found."},
            status=401
        )
    if authorised_account.type is not enums.AccountType.OWNER:
        return aiohttp.web.json_response(
            {"error": "You do not have permission to create accounts."},
            status=403
        )

    body = await request.json()

    try:
        username = utils.get_body_field(body, "username")
        email = utils.get_body_field(body, "email")
        password = utils.get_body_field(body, "password")
        bot = utils.get_body_field(body, "bot")
    except exceptions.MissingFieldError as error:
        return aiohttp.web.json_response(
            {"error": error.message},
            status=error.status
        )

    id = snowflake.generate_snowflake()
    token = f"{'bot' if bot is True else 'user'}.{username}.{id}.{binascii.hexlify(os.urandom(32)).decode('utf-8')}"

    try:
        data = await app.db.fetchrow(
                "INSERT INTO accounts (id, username, token, bot, email, password, type) VALUES ($1, $2, $3, $4, $5, $6, crypt($7, gen_salt($8))) RETURNING *",
                id, username, token, bot, email, password, "bf", body.get("type", 0)
        )
    except asyncpg.exceptions.UniqueViolationError:
        return aiohttp.web.json_response(
            {"error": f"The email '{email}' is already registered."},
            status=400
        )

    account = objects.Account(data)

    return aiohttp.web.json_response(
        account.info,
        status=201
    )


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.post(r"/api/accounts", create_account)])  # type: ignore
