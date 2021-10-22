# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

# My stuff
from core.app import CDN


@aiohttp_jinja2.template("login.html")  # type: ignore
async def login(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    session = await aiohttp_session.get_session(request)
    app: CDN = request.app  # type: ignore

    if (await app.get_account(session)) is not None:
        return aiohttp.web.HTTPFound("/")

    return None


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/login", login)])  # type: ignore
