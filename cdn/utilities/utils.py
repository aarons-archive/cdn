# Future
from __future__ import annotations

# Standard Library
import datetime as dt
import re
from collections.abc import Sequence
from typing import Any, Literal

# Packages
import aiohttp.web
import asyncpg.exceptions
import humanize
import pendulum

# My stuff
from utilities import exceptions


class _MissingSentinel:

    def __eq__(self, other: Any) -> Literal[False]:
        return False

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()


def convert_datetime(datetime: dt.datetime | pendulum.DateTime, /) -> pendulum.DateTime:

    datetime.replace(microsecond=0)

    if type(datetime) is dt.datetime and datetime.tzinfo == dt.timezone.utc:
        datetime = datetime.replace(tzinfo=None)

    return pendulum.instance(datetime, tz="UTC")


def format_datetime(datetime: dt.datetime | pendulum.DateTime, /, *, seconds: bool = False) -> str:
    return convert_datetime(datetime).format(f"dddd MMMM Do YYYY [at] hh:mm{':ss' if seconds else ''} A")


def format_date(date: pendulum.Date, /) -> str:
    return date.format("dddd MMMM Do YYYY")


def format_time(time: pendulum.Time, /) -> str:
    return time.format("hh:mm:ss")


def format_difference(datetime: dt.datetime | pendulum.DateTime, /, *, suppress: tuple[str] = ("seconds",)) -> str:

    datetime = convert_datetime(datetime)

    now = pendulum.now(tz=datetime.timezone)
    now.replace(microsecond=0)

    return humanize.precisedelta(now.diff(datetime), format="%0.0f", suppress=suppress)


def format_seconds(seconds: float, /, *, friendly: bool = False) -> str:

    seconds = round(seconds)

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly is True:
        return f"{f'{days}d ' if not days == 0 else ''}{f'{hours}h ' if not hours == 0 or not days == 0 else ''}{minutes}m {seconds}s"

    return f"{f'{days:02d}:' if not days == 0 else ''}{f'{hours:02d}:' if not hours == 0 or not days == 0 else ''}{minutes:02d}:{seconds:02d}"


UNIQUE_VIOLATION_ERROR_REGEX: re.Pattern[str] = re.compile(r"Key \((?P<column>.+)\)=\((?P<value>.+)\) already exists.")


def get_unique_violation_error_details(error: asyncpg.exceptions.UniqueViolationError, /) -> Sequence[str]:

    if match := re.match(UNIQUE_VIOLATION_ERROR_REGEX, error.detail):  # type: ignore
        return match.groups()

    raise exceptions.JSONResponseError(
        "a value passed already exists in the database.",
        status=400
    )


def get_body_field(body: dict[str, Any], /, *, field: str) -> Any:

    if value := body.get(field):
        return value

    raise exceptions.JSONResponseError(
        f"request body must have the '{field}' field.",
        status=400
    )


def check_body_is_readable(readable: bool, /) -> None:

    if not readable:
        raise exceptions.JSONResponseError(
            "request body must not be empty.",
            status=400
        )


def check_content_type(received: str, /, *, expected: str) -> None:

    if expected != received:
        raise exceptions.JSONResponseError(
            f"'Content-Type' header was invalid, expected '{expected}' but received '{received}'.",
            status=400
        )
