import sys

from loguru import logger


def setup_logging(level: str) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    )
