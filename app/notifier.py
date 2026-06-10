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
def _get_webhook_urls(settings: Settings) -> list[str]:
    return settings.all_discord_webhook_urls


def send_game_notification(settings: Settings, game: Game) -> None:
    webhook_urls = _get_webhook_urls(settings)
    if not webhook_urls:
        logger.warning(
            "Discord webhook URL not configured; skipping notification for {}",
            game.name,
        )
        return

    payload = _build_payload(settings, game)
    success_count = 0
    failures: list[str] = []

    for webhook_url in webhook_urls:
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                impersonate="chrome",
                timeout=15,
            )
        except requests.RequestsError as exc:
            logger.error(
                "Network error sending Discord notification for {} to {}: {}",
                game.name,
                webhook_url,
                exc,
            )
            failures.append(webhook_url)
            continue

        if response.status_code not in (200, 204):
            logger.error(
                "Discord webhook returned HTTP {} for {} to {}",
                response.status_code,
                game.name,
                webhook_url,
            )
            failures.append(webhook_url)
            continue

        success_count += 1
        logger.info("Discord notification sent for {} to {}", game.name, webhook_url)

    if success_count == 0:
        raise NotifierError("Discord notification failed for all configured webhooks")

    if failures:
        logger.warning(
            "Discord notification delivered to {} of {} webhooks for {}",
            success_count,
            len(webhook_urls),
            game.name,
        )
