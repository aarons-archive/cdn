# Future
from __future__ import annotations

# My stuff
from core import config
from utilities import enums


EPOCH = 1601510400
BASE_URL = f"http://{config.HOST}:{config.PORT}/" if config.ENV is enums.Environment.DEVELOPMENT else f"https://cdn.axelancerr.xyz/"


def redirect_uri(path: str) -> str:
    return f"{BASE_URL}{path[1:]}"
