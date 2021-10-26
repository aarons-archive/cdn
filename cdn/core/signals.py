# Future
from __future__ import annotations

# Standard Library
import importlib
import os

# Packages
import aiohttp
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session
import jinja2
from aiohttp_session import redis_storage

# My stuff
from core import config
from core.app import CDN


async def start(app: aiohttp.web.Application) -> None:

    aiohttp_session.setup(
        app=app,
        storage=redis_storage.RedisStorage(app.redis)  # type: ignore
    )

    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader(searchpath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates")))
    )

    app.add_routes(
        [
            aiohttp.web.static(
                prefix="/app/static",
                path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
                show_index=True,
                follow_symlinks=True,
                append_version=True,
            )
        ]
    )
    app["static_root_url"] = "/app/static"

    for module in [importlib.import_module(f"endpoints.{endpoint}") for endpoint in config.ENDPOINTS]:
        module.setup(app=app)  # type: ignore


def setup(app: CDN) -> None:
    app.on_startup.extend([start])
