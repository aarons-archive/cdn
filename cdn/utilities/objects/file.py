# Future
from __future__ import annotations

# Standard Library
import datetime
from typing import TYPE_CHECKING

# My stuff
from utilities import objects


if TYPE_CHECKING:
    # Packages
    from app import AxelWeb


class File:

    __slots__ = "_app", "_account", "_account_id", "_identifier", "_format", "_created_at"

    def __init__(self, app: AxelWeb, account: objects.Account, data: dict) -> None:

        self._app: AxelWeb = app
        self._account: objects.Account = account

        self._account_id: int = data.get("account_id")
        self._identifier: str = data.get("identifier")
        self._format: str = data.get("format")
        self._created_at: datetime.datetime = data.get("created_at")

    def __repr__(self) -> str:
        return f"<axelweb.File identifier={self.identifier} format={self.format} account={self.account}>"

    # Properties

    @property
    def app(self) -> AxelWeb:
        return self._app

    @property
    def account(self) -> objects.Account:
        return self._account

    @property
    def account_id(self) -> int:
        return self._account_id

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def format(self) -> str:
        return self._format

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    #

    @property
    def filename(self) -> str:
        return f"{self.identifier}.{self.format}"
