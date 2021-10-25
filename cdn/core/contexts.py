# Future
from __future__ import annotations

# Standard Library
from collections.abc import AsyncGenerator

# Packages
import aiohttp.web
import aioredis
import asyncpg
import asyncpg.exceptions

# My stuff
from core import config
from core.app import CDN


async def asyncpg_connect(app: aiohttp.web.Application) -> AsyncGenerator[None, None]:

    try:
        db: asyncpg.Pool = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)  # type: ignore
    except asyncpg.exceptions.PostgresConnectionError:
        raise ConnectionError()

    app.db = db

    yield

    await db.close()


async def aioredis_connect(app: aiohttp.web.Application) -> AsyncGenerator[None, None]:

    try:
        redis = aioredis.from_url(url=config.REDIS, retry_on_timeout=True)
    except aioredis.RedisError:
        raise ConnectionError()

    app.redis = redis

    yield

    await redis.close()


def setup(app: CDN) -> None:
    app.cleanup_ctx.extend([asyncpg_connect, aioredis_connect])
