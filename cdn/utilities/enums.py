# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "Environment",
    "AccountType"
)


class Environment(Enum):
    PRODUCTION = 1
    DEVELOPMENT = 2


class AccountType(Enum):
    USER = 0
    MODERATOR = 1
    ADMIN = 2
    OWNER = 3
