# Future
from __future__ import annotations

# Standard Library
from collections.abc import Awaitable, Callable

# Packages
import aiohttp
import aiohttp.web
import aiohttp_jinja2

# My stuff
from core.app import CDN
from utilities import exceptions


@aiohttp.web.middleware
async def middleware(request: aiohttp.web.Request, handler: Callable[[aiohttp.web.Request], Awaitable[aiohttp.web.StreamResponse]]):

    try:
        return await handler(request)

    except exceptions.JSONResponseError as error:
        return aiohttp.web.json_response({"error": error.message}, status=error.status)

    except aiohttp.web.HTTPException as error:

        match error.status:
            case 404:
                return aiohttp_jinja2.render_template("404.html", request, {}, status=404)
            case _:
                return aiohttp_jinja2.render_template("500.html", request, {}, status=500)


def setup(app: CDN) -> None:
    app.middlewares.extend([middleware])
