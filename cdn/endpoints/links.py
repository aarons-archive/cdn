# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web

# My stuff
from core import values


async def github(_: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:
    return aiohttp.web.HTTPFound(values.GITHUB_URL)


async def discord(_: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:
    return aiohttp.web.HTTPFound(values.DISCORD_URL)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/github", github),  # type: ignore
            aiohttp.web.get(r"/discord", discord),  # type: ignore
        ]
    )
