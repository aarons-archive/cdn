# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_session

# My stuff
from core.app import CDN
from utilities import exceptions, utils


async def login(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    session = await aiohttp_session.new_session(request)
    app: CDN = request.app  # type: ignore

    utils.check_body_is_readable(request.can_read_body)
    utils.check_content_type(request.content_type, expected="application/x-www-form-urlencoded")

    data = await request.post()

    account = await app.db.fetchrow(
        "SELECT * FROM accounts WHERE username = $1 and password = crypt($2, password)",
        data["username"], data["password"]
    )

    if not account:
        raise exceptions.JSONResponseError("An account with that username and password combination does not exist.", status=403)

    session["token"] = account["token"]
    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.post(r"/api/login", login),
        ]
    )
