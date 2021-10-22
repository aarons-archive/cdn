# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import pendulum


class File:

    def __init__(self, data: dict[str, Any], /) -> None:

        self._account_id: int = data["account_id"]
        self._identifier: str = data["identifier"]
        self._format: str = data["format"]
        self._created_at: pendulum.DateTime = pendulum.instance(data["created_at"], tz="UTC")
        self._private: bool = data["private"]

    def __repr__(self) -> str:
        return f"<cdn.File identifier='{self.identifier}' format='{self.format}' private={self.private}>"

    # Properties

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
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def private(self) -> bool:
        return self._private

    #

    @property
    def filename(self) -> str:
        return f"{self.identifier}.{self.format}"
