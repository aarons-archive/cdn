# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session


@aiohttp_jinja2.template("login.html")  # type: ignore
async def login(request: aiohttp.web.Request) -> aiohttp.web.Response | dict[str, Any]:

    session = await aiohttp_session.get_session(request)

    if session.get("token"):
        return aiohttp.web.HTTPFound("/")

    return {}


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/login", login),  # type: ignore
        ]
    )
