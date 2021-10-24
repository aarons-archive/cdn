# Future
from __future__ import annotations

# Standard Library
import binascii
import os

# Packages
import aiohttp
import aiohttp.web
import asyncpg.exceptions

# My stuff
from core.app import CDN
from utilities import enums, exceptions, objects, snowflake, utils


async def post(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    if authorised_account.type is not enums.AccountType.OWNER:
        raise exceptions.JSONResponseError("You do not have permission to create accounts.", status=403)

    utils.check_body_is_readable(request.can_read_body)
    utils.check_content_type(request.content_type, expected="application/json")

    body = await request.json()

    password = utils.get_body_field(body, field="password")
    username = utils.get_body_field(body, field="username")
    email = utils.get_body_field(body, field="email")

    id = snowflake.generate_snowflake()
    token = f"{username}.{id}.{binascii.hexlify(os.urandom(32)).decode('utf-8')}"

    try:
        data = await app.db.fetchrow(
                "INSERT INTO accounts (id, password,                  token, username, email, bot, type, avatar) "
                "VALUES               ($1, crypt($2, gen_salt('bf')), $3,    $4,       $5,    $6,  $7,   $8    )"
                "RETURNING *",
                id, password, token, username, email, body.get("bot", False), body.get("type", 0), body.get("avatar", "")
        )

    except asyncpg.exceptions.UniqueViolationError as error:
        column, value = utils.get_unique_violation_error_details(error)
        raise exceptions.JSONResponseError(f"{column} '{value}' is already in-use", status=400)

    account = objects.Account(data)
    return aiohttp.web.json_response(account.info, status=201)


async def get(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not await app.fetch_account_by_token(token):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    id = request.match_info["id"]

    if not (account := await app.fetch_account_by_id(int(id))):
        raise exceptions.JSONResponseError(f"account with id {id} does not exist.", status=401)

    return aiohttp.web.json_response(account.partial_info)


async def patch(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    if authorised_account.type is not enums.AccountType.OWNER:
        raise exceptions.JSONResponseError("You do not have permission to edit accounts.", status=403)

    id = request.match_info["id"]

    if not (account := await app.fetch_account_by_id(int(id))):
        raise exceptions.JSONResponseError(f"account with id {id} does not exist.", status=401)

    # TODO: File editing options here.
    return aiohttp.web.json_response(account.partial_info)


async def delete(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: CDN = request.app  # type: ignore

    if not (token := request.headers.get("Authorization")):
        raise exceptions.JSONResponseError("'Authorization' header token is missing.", status=400)
    if not (authorised_account := await app.fetch_account_by_token(token)):
        raise exceptions.JSONResponseError("'Authorization' header token is invalid or has expired.", status=401)

    if authorised_account.type is not enums.AccountType.OWNER:
        raise exceptions.JSONResponseError("You do not have permission to delete accounts.", status=403)

    id = request.match_info["id"]

    if not (account := await app.fetch_account_by_id(int(id))):
        raise exceptions.JSONResponseError(f"account with id {id} does not exist.", status=401)

    # TODO: Probably add some kind of additional check? idk
    await app.db.execute("DELETE FROM accounts WHERE id = $1", account.id)

    return aiohttp.web.json_response(status=204)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.post(r"/api/v1/accounts", post),
            aiohttp.web.get(r"/api/v1/accounts/{id:\d+}", get),
            aiohttp.web.patch(r"/api/v1/accounts/{id:\d+}", patch),
            aiohttp.web.delete(r"/api/v1/accounts/{id:\d+}", delete),
        ]
    )
