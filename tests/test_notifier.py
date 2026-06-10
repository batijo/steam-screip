from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from app.config import Settings
from app.models import Game
from app.notifier import send_game_notification


@dataclass
class DummyResponse:
    status_code: int


class DummyRequests:
    def __init__(self):
        self.posts = []

    def post(self, url, json, impersonate, timeout):
        self.posts.append((url, json, impersonate, timeout))
        return DummyResponse(status_code=204)


@pytest.fixture
def settings() -> Settings:
    return Settings(discord_webhook_urls="https://example.com/a, https://example.com/b")


@pytest.fixture
def game() -> Game:
    return Game(
        name="Gravity Circuit",
        steam_url="https://store.steampowered.com/app/858710/",
        discovered_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def dummy_requests(monkeypatch):
    requests = DummyRequests()
    monkeypatch.setattr("app.notifier.requests", requests)
    return requests


def test_settings_parses_discord_webhook_urls_from_comma_string() -> None:
    settings = Settings(discord_webhook_urls="https://example.com/a, https://example.com/b")

    assert settings.discord_webhook_urls == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert settings.all_discord_webhook_urls == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_all_discord_webhook_urls_deduplicates_old_and_new_values() -> None:
    settings = Settings(
        discord_webhook_url="https://example.com/a",
        discord_webhook_urls=["https://example.com/a", "https://example.com/b"],
    )

    assert settings.all_discord_webhook_urls == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_send_game_notification_posts_to_multiple_webhooks(dummy_requests, settings, game) -> None:
    send_game_notification(settings, game)

    assert len(dummy_requests.posts) == 2
    assert dummy_requests.posts[0][0] == "https://example.com/a"
    assert dummy_requests.posts[1][0] == "https://example.com/b"
