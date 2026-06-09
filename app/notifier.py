from curl_cffi import requests
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings
from app.models import Game


class NotifierError(Exception):
    pass


def _build_payload(settings: Settings, game: Game) -> dict:
    template = settings.discord_message_template.replace("\\n", "\n")
    payload: dict = {
        "username": settings.discord_username,
        "content": template.format(
            name=game.name,
            steam_url=game.steam_url,
        ),
    }
    if settings.discord_avatar_url:
        payload["avatar_url"] = settings.discord_avatar_url
    return payload


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((NotifierError, requests.RequestsError)),
)
def send_game_notification(settings: Settings, game: Game) -> None:
    if not settings.discord_webhook_url:
        logger.warning(
            "Discord webhook URL not configured; skipping notification for {}",
            game.name,
        )
        return

    payload = _build_payload(settings, game)

    try:
        response = requests.post(
            settings.discord_webhook_url,
            json=payload,
            impersonate="chrome",
            timeout=15,
        )
    except requests.RequestsError as exc:
        logger.error("Network error sending Discord notification for {}: {}", game.name, exc)
        raise

    if response.status_code not in (200, 204):
        logger.error(
            "Discord webhook returned HTTP {} for {}",
            response.status_code,
            game.name,
        )
        raise NotifierError(f"Discord webhook returned HTTP {response.status_code}")

    logger.info("Discord notification sent for {}", game.name)
