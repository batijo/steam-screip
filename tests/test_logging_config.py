from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger

from app.logging_config import _LOG_FORMAT, setup_logging


def test_log_format_is_plain_timestamp() -> None:
    assert _LOG_FORMAT == "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"


def test_setup_logging_uses_configured_timezone(capsys) -> None:
    setup_logging("INFO", "Europe/Berlin")
    logger.info("test")

    line = capsys.readouterr().err.splitlines()[0]
    logged_time_str = line.split(" | ", maxsplit=1)[0]
    logged_time = datetime.strptime(logged_time_str, "%Y-%m-%d %H:%M:%S")
    expected = datetime.now(ZoneInfo("Europe/Berlin")).replace(tzinfo=None)
    assert abs((logged_time - expected).total_seconds()) < 2
    assert "| INFO     | test" in line


def test_setup_logging_does_not_corrupt_timestamp(capsys) -> None:
    setup_logging("INFO", "Europe/Berlin")
    logger.info("test")

    line = capsys.readouterr().err.splitlines()[0]
    assert "!Europe" not in line
    assert "!4urope" not in line
    assert "| INFO     | test" in line
