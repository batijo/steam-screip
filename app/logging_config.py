import sys
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger

_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"


def _timezone_formatter(zone: ZoneInfo) -> Callable[[dict], str]:
    def formatter(record: dict) -> str:
        timestamp = datetime.now(zone).strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} | {record['level'].name:<8} | {record['message']}\n"
        if record["exception"]:
            line += f"{record['exception']}\n"
        return line

    return formatter


def setup_logging(level: str, timezone: str = "") -> None:
    logger.remove()

    tz = timezone.strip()
    if tz and tz.lower() != "local":
        logger.add(
            sys.stderr,
            format=_timezone_formatter(ZoneInfo(tz)),
            level=level.upper(),
        )
    else:
        logger.add(
            sys.stderr,
            level=level.upper(),
            format=_LOG_FORMAT,
        )
