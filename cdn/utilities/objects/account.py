# Future
from __future__ import annotations

# Standard Library
import time
from typing import Any

# My stuff
from utilities import enums


class Account:

    def __init__(self, data: dict[str, Any], /) -> None:

        self._id: int = data["id"]
        self._password: str = data["password"]
        self._token: str = data["token"]
        self._username: str = data["username"]
        self._email: str = data["email"]
        self._bot: bool = data["bot"]
        self._type: enums.AccountType = enums.AccountType(data["type"])
        self._avatar: str = data["avatar"]

        self._fetched_at: float = data.get("fetched_at", time.time())

    def __repr__(self) -> str:
        return f"<cdn.Account username={self.username}>"

    # Properties

    @property
    def id(self) -> int:
        return self._id

    @property
    def password(self) -> str:
        return self._password

    @property
    def token(self) -> str:
        return self._token

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def type(self) -> enums.AccountType:
        return self._type

    @property
    def avatar(self) -> str:
        return self._avatar

    #

    @property
    def fetched_at(self) -> float:
        return self._fetched_at

    def is_expired(self) -> bool:
        return (time.time() - self.fetched_at) > 10

    #

    @property
    def partial_info(self) -> dict[str, Any]:

        return {
            "id":         self.id,
            "username":   self.username,
            "bot":        self.bot,
            "type":       self.type.value,
            "avatar":     self.avatar,
            "fetched_at": self.fetched_at
        }

    @property
    def info(self) -> dict[str, Any]:
        return self.partial_info | {"password": self.password, "token": self.token, "email": self.email}
