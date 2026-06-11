import sys

from loguru import logger


def _log_time_format(timezone: str) -> str:
    tz = timezone.strip()
    if not tz or tz.lower() == "local":
        time_token = "{time:YYYY-MM-DD HH:mm:ss}"
    else:
        time_token = f"{{time:YYYY-MM-DD HH:mm:ss!{tz}}}"
    return f"{time_token} | {{level:<8}} | {{message}}"


def setup_logging(level: str, timezone: str = "") -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=_log_time_format(timezone),
    )
