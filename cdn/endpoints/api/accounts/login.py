# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_session

# My stuff
from core.app import CDN


async def login(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    session = await aiohttp_session.get_session(request)
    app: CDN = request.app  # type: ignore

    if not request.can_read_body:
        return aiohttp.web.json_response(
            {"error": "request body must not be empty."},
            status=400
        )
    if request.content_type != "application/x-www-form-urlencoded":
        return aiohttp.web.json_response(
            {"error": f"expected content-type 'application/x-www-form-urlencoded', received '{request.content_type}'"},
            status=400
        )

    data = await request.post()

    if not (username := data.get("username")):
        return aiohttp.web.json_response(
            {"error": "The 'username' field is required."},
            status=400
        )

    if not (password := data.get("password")):
        return aiohttp.web.json_response(
            {"error": "The 'password' field is required."},
            status=400
        )

    account = await app.db.fetchrow(
        "SELECT * FROM accounts WHERE username = $1 and (password = crypt($2, password))",
        username, password
    )

    if not account:
        return aiohttp.web.json_response(
            {"error": "An accounts with that username and password combination was not found."},
            status=401
        )

    session["token"] = account["token"]
    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.post(r"/api/accounts/login", login)])  # type: ignore
