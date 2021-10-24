# Future
from __future__ import annotations

# Standard Library
import importlib
import logging
import os
from collections.abc import Awaitable, Callable

# Packages
import aiohttp
import aiohttp.client
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session
import aioredis
import asyncpg
import jinja2
from aiohttp_session import redis_storage

# My stuff
from core import config
from utilities import exceptions, objects, utils


__log__: logging.Logger = logging.getLogger("cdn")


class CDN(aiohttp.web.Application):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, middlewares=[self.middleware])

        self.db: asyncpg.Pool = utils.MISSING
        self.redis: aioredis.Redis = utils.MISSING

    # Cleanup context

    async def asyncpg_connect(self, _: aiohttp.web.Application) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)
        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()

        __log__.info("[POSTGRESQL] Successful connection.")
        self.db = db

        yield

        __log__.info("[POSTGRESQL] Closing connection.")
        await self.db.close()

    async def aioredis_connect(self, _: aiohttp.web.Application) -> None:

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, retry_on_timeout=True)
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()

        __log__.info("[REDIS] Successful connection.")
        self.redis = redis

        yield

        __log__.info("[REDIS] Closing connection.")
        await self.redis.close()

    # Signals

    async def start(self, _: aiohttp.web.Application) -> None:

        aiohttp_session.setup(
            app=self,
            storage=redis_storage.RedisStorage(self.redis)
        )

        aiohttp_jinja2.setup(
            app=self,
            loader=jinja2.FileSystemLoader(searchpath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates")))
        )

        self.add_routes(
            [
                aiohttp.web.static(
                    prefix="/static",
                    path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
                    show_index=True,
                    follow_symlinks=True,
                    append_version=True,
                )
            ]
        )
        self["static_root_url"] = "/static"

        for module in [importlib.import_module(f"endpoints.{endpoint}") for endpoint in config.ENDPOINTS]:
            module.setup(self)  # type: ignore

    # Middlewares

    @aiohttp.web.middleware
    async def middleware(self, request: aiohttp.web.Request, handler: Callable[[aiohttp.web.Request], Awaitable[aiohttp.web.StreamResponse]]):

        try:
            response = await handler(request)
        except exceptions.JSONResponseError as error:
            response = aiohttp.web.json_response({"error": error.message}, status=error.status)

        return response

    #

    async def fetch_account(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.Account | None:

        if not (data := await self.db.fetchrow("SELECT * FROM accounts WHERE token = $1", session.get("token"))):
            return None

        account = objects.Account(data)
        session["accounts"] = account.info

        return account

    async def fetch_account_by_token(
        self,
        token: str,
        /
    ) -> objects.Account | None:

        if not (data := await self.db.fetchrow("SELECT * FROM accounts WHERE token = $1", token)):
            return None

        return objects.Account(data)

    async def fetch_account_by_id(
        self,
        id: int,
        /
    ) -> objects.Account | None:

        if not (data := await self.db.fetchrow("SELECT * FROM accounts WHERE id = $1", id)):
            return None

        return objects.Account(data)

    async def get_account(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.Account | None:

        if not session.get("token"):
            return None

        if not (data := session.get("accounts")):
            return await self.fetch_account(session)

        account = objects.Account(data)
        if account.is_expired():
            account = await self.fetch_account(session)

        return account

    async def get_files(
        self,
        session: aiohttp_session.Session,
        /
    ) -> list[objects.File] | None:

        if not (account := await self.get_account(session)):
            return None

        if not (files := await self.db.fetch("SELECT * FROM files WHERE account_id = $1 ORDER BY id DESC", account.id)):
            return None

        return [objects.File(file) for file in files]

    async def get_file_owned_by(
        self,
        identifier: int,
        /,
        *,
        id: int
    ) -> objects.File | None:

        if not (file := await self.db.fetchrow("SELECT * FROM files WHERE identifier = $1 AND account_id = $2", identifier, id)):
            return None

        return objects.File(file)
