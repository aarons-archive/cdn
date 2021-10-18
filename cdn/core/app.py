# Future
from __future__ import annotations

# Standard Library
import logging

# Packages
import aiohttp
import aiohttp.client
import aiohttp.web
import aioredis
import asyncpg

# My stuff
from core import config
from utilities import objects


__log__: logging.Logger = logging.getLogger("cdn")


class CDN(aiohttp.web.Application):

    def __init__(self) -> None:
        super().__init__()

        self.db: asyncpg.Pool | None = None
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

        accounts = await self.db.fetch("SELECT * FROM accounts")

        for account in accounts:
            self.accounts[account["id"]] = objects.Account(app=self, data=account)
        __log__.info(f"[ACCOUNTS] Loaded accounts [{len(accounts)} accounts]")

        files = await self.db.fetch("SELECT * FROM files")

        for file in files:
            account = self.accounts[file["account_id"]]
            account._files[file["identifier"]] = objects.File(app=self, account=account, data=file)

        __log__.info(f"[FILES] Loaded files [{len(files)} files]")

    #

    def get_account_by_id(self, id: int) -> objects.Account | None:
        return self.accounts.get(id)

    def get_account_by_token(self, token: str) -> objects.Account | None:

        if not token:
            return None

        if not (accounts := [account for account in self.accounts.values() if account.token == token]):
            return None

        return accounts[0]

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
