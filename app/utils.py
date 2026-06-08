import re

APP_ID_PATTERN = re.compile(r"/app/(\d+)")


def extract_app_id(steam_url: str) -> str | None:
    match = APP_ID_PATTERN.search(steam_url)
    return match.group(1) if match else None
