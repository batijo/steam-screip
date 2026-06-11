import os
from io import StringIO

from loguru import logger

from app.logging_config import _LOG_FORMAT, setup_logging


def test_log_format_is_plain_timestamp() -> None:
    assert _LOG_FORMAT == "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"


def test_setup_logging_applies_timezone(monkeypatch) -> None:
    monkeypatch.delenv("TZ", raising=False)
    setup_logging("INFO", "Europe/Vilnius")
    assert os.environ["TZ"] == "Europe/Vilnius"


def test_setup_logging_does_not_corrupt_timestamp(monkeypatch) -> None:
    monkeypatch.delenv("TZ", raising=False)
    setup_logging("INFO", "Europe/Vilnius")

    stream = StringIO()
    logger.remove()
    logger.add(stream, format=_LOG_FORMAT)
    logger.info("test")

    line = stream.getvalue()
    assert "!Europe" not in line
    assert "!4urope" not in line
    assert "Vilniu" not in line
    assert "| INFO     | test" in line
