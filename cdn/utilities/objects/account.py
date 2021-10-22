# Future
from __future__ import annotations

# Standard Library
import datetime as dt
import time
from typing import Any

# Packages
import pendulum

# My stuff
from utilities import enums, objects


class Account:

    def __init__(self, data: dict[str, Any], /) -> None:

        self._id: int = data["id"]
        self._username: str = data["username"]
        self._token: str = data["token"]
        self._bot: bool = data["bot"]
        self._email: str = data["email"]
        self._password: str = data["password"]

        _created_at = data["created_at"]
        self._created_at: pendulum.DateTime = pendulum.instance(
            _created_at if isinstance(_created_at, dt.datetime) else dt.datetime.fromisoformat(_created_at),
            tz="UTC"
        )

        self._type: enums.AccountType = enums.AccountType(data["type"])

        self._fetched_at: float = data.get("fetched_at", time.time())
        self._files: dict[str, objects.File] = {}

    def __repr__(self) -> str:
        return f"<cdn.Account id={self.id}, username='{self.username}', bot={self.bot}, type={self.type}>"

    # Properties

    @property
    def id(self) -> int:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def token(self) -> str:
        return self._token

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    @property
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def type(self) -> enums.AccountType:
        return self._type

    #

    @property
    def fetched_at(self) -> float:
        return self._fetched_at

    def is_expired(self) -> bool:
        return (time.time() - self.fetched_at) > 10

    #

    @property
    def files(self) -> dict[str, objects.File]:
        return self._files

    #

    @property
    def partial_info(self) -> dict[str, Any]:
        return {
            "id":         self.id,
            "username":   self.username,
            "bot":        self.bot,
            "created_at": self.created_at.isoformat(),
            "type":       self.type.value,
            "fetched_at": self.fetched_at
        }

    @property
    def info(self) -> dict[str, Any]:
        return self.partial_info | {"token": self.token, "email": self.email, "password": self.password}
