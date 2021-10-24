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


@aiohttp_jinja2.template("media.html")  # type: ignore
async def media(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    session = await aiohttp_session.get_session(request)
    app: CDN = request.app  # type: ignore

    account = await app.get_account(session)
    files = await app.get_files(session)

    return {
        "account": account.info if account else None,
        "files": [file.info for file in files] if files else None
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/app/media", media),  # type: ignore
        ]
    )
