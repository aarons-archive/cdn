# Future
from __future__ import annotations

# Packages
import aiohttp.web

# My stuff
from core import values


async def github(_: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.HTTPFound(values.GITHUB_URL)


async def discord(_: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.HTTPFound(values.DISCORD_URL)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/app/github", github),  # type: ignore
            aiohttp.web.get(r"/app/discord", discord),  # type: ignore
        ]
    )
