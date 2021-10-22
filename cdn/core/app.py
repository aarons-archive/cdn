# Future
from __future__ import annotations

# Standard Library
import logging

# Packages
import aiohttp
import aiohttp.client
import aiohttp.web
import aiohttp_session
import aioredis
import asyncpg
from aiohttp_session import redis_storage

# My stuff
from core import config
from utilities import objects, utils


__log__: logging.Logger = logging.getLogger("cdn")


class CDN(aiohttp.web.Application):

    def __init__(self) -> None:
        super().__init__()

        self.db: asyncpg.Pool = utils.MISSING
        self.redis: aioredis.Redis | None = None

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.words: list[str] = []
        self.accounts: dict[int, objects.Account] = {}

        self.on_startup.append(self.start)

    async def start(self, _) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)
        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[POSTGRESQL] Successful connection.")
            self.db = db

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, retry_on_timeout=True)
            await redis.ping()
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[REDIS] Successful connection.")
            self.redis = redis

        aiohttp_session.setup(
            app=self,
            storage=redis_storage.RedisStorage(redis)
        )

    #

    async def fetch_account(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.Account | None:

        if not (data := await self.db.fetchrow("SELECT * FROM accounts WHERE token = $1", session.get("token"))):
            return None

        account = objects.Account(data)
        session["account"] = account.info

        return account

    async def get_account(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.Account | None:

        if not session.get("token"):
            return None

        if not (data := session.get("account")):
            return await self.fetch_account(session)

        account = objects.Account(data)
        if account.is_expired():
            account = await self.fetch_account(session)

        return account

    #

    async def get_file(self, *, identifier: str) -> objects.File | None:

        if identifier is None:
            return None

        file_data = await self.db.fetchrow("SELECT * FROM files WHERE identifier = $1", identifier)
        if not file_data:
            return None

        return objects.File(data=dict(file_data))

    async def get_account_files(self, account_id: int) -> list[objects.File] | None:

        files = await self.db.fetch("SELECT * FROM files WHERE account_id = $1 ORDER BY created_at DESC", account_id)
        if not files:
            return None

        return [objects.File(data=dict(file)) for file in files]
