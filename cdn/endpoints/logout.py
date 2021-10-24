# Future
from __future__ import annotations

# Packages
import aiohttp.web
import aiohttp_session


async def logout(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.get_session(request)

    if not session.get("token"):
        return aiohttp.web.HTTPFound("/app")

    del session["token"]
    return aiohttp.web.HTTPFound("/app")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/app/logout", logout),  # type: ignore
        ]
    )
