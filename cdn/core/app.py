# Future
from __future__ import annotations

# Standard Library
import logging

# Packages
import aiohttp.web
import aiohttp_session
import aioredis
import asyncpg

# My stuff
from utilities import objects, utils


__log__: logging.Logger = logging.getLogger("cdn")


class CDN(aiohttp.web.Application):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.db: asyncpg.Pool = utils.MISSING
        self.redis: aioredis.Redis = utils.MISSING

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

    #

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
        identifier: str,
        /,
        *,
        id: int
    ) -> objects.File | None:

        if not (file := await self.db.fetchrow("SELECT * FROM files WHERE identifier = $1 AND account_id = $2", identifier, id)):
            return None

        return objects.File(file)
