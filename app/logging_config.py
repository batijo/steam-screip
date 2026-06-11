import os
import sys
import time

from loguru import logger

_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"


def setup_logging(level: str, timezone: str = "") -> None:
    tz = timezone.strip()
    if tz and tz.lower() != "local":
        os.environ["TZ"] = tz
        if hasattr(time, "tzset"):
            time.tzset()

    logger.remove()
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=_LOG_FORMAT,
    )
