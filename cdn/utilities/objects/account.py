# Future
from __future__ import annotations

# Standard Library
import datetime

# My stuff
from utilities import enums, objects


class Account:

    def __init__(
        self,
        data: dict,
        /
    ) -> None:

        self._id: int = data['id']
        self._username: str = data.get('username')
        self._token: str = data.get('token')
        self._bot: bool = data.get('bot')
        self._email: str = data.get('email')
        self._password: str = data.get('password')
        self._created_at: datetime.datetime = data.get('created_at')
        self._type: enums.AccountType = enums.AccountType(data.get('type'))

        self._files: dict[str, objects.File] = {}

    def __repr__(self) -> str:
        return f'<axelweb.Account id=\'{self.id}\' username=\'{self.username}\' bot={self.bot}>'

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
    def type(self) -> enums.AccountType:
        return self._type

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    #

    @property
    def files(self) -> dict[str, objects.File]:
        return self._files

    #

    @property
    def partial_info(self) -> dict:
        return {
            'id':       self.id,
            'username': self.username,
            'bot':      self.bot,
            'created_at': self.created_at.isoformat()
        }

    @property
    def info(self) -> dict:
        return self.partial_info | {'token': self.token, 'email': self.email}
