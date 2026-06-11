from app.logging_config import _log_time_format


def test_log_time_format_uses_iana_timezone() -> None:
    fmt = _log_time_format("Europe/Ljubljana")
    assert fmt == "{time:YYYY-MM-DD HH:mm:ss!Europe/Ljubljana} | {level:<8} | {message}"


def test_log_time_format_local_uses_plain_timestamp() -> None:
    fmt = _log_time_format("local")
    assert fmt == "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"


def test_log_time_format_empty_uses_plain_timestamp() -> None:
    fmt = _log_time_format("")
    assert fmt == "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
