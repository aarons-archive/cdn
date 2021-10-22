# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_session


async def logout(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    session = await aiohttp_session.get_session(request)

    if not session.get("token"):
        return aiohttp.web.json_response(
            {"error": "You are not logged in."}
        )

    del session["token"]
    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.post(r"/api/account/logout", logout)])  # type: ignore
