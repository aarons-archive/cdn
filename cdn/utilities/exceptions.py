# Future
from __future__ import annotations


class JSONResponseError(Exception):

    def __init__(self, message: str, status: int) -> None:

        self._message: str = message
        self._status: int = status

    @property
    def message(self) -> str:
        return self._message

    @property
    def status(self) -> int:
        return self._status
