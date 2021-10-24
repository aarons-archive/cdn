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


@aiohttp_jinja2.template("index.html")  # type: ignore
async def index(request: aiohttp.web.Request) -> dict[str, Any]:

    session = await aiohttp_session.get_session(request)
    app: CDN = request.app  # type: ignore

    account = await app.get_account(session)

    return {
        "account": account.info if account else None
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/", index),  # type: ignore
        ]
    )
