from pathlib import Path

import pytest

from app.config import Settings
from app.parser import parse_free_games

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "steamdb.html"


@pytest.fixture
def settings() -> Settings:
    return Settings()


def test_parse_free_games_extracts_only_100_percent_discounts(settings: Settings) -> None:
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    games = parse_free_games(settings, html_content)

    assert len(games) == 2
    names = {game.name for game in games}
    assert names == {"Gravity Circuit", "Tell Me Why"}


def test_parse_free_games_extracts_correct_urls(settings: Settings) -> None:
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    games = parse_free_games(settings, html_content)

    gravity = next(game for game in games if game.name == "Gravity Circuit")
    assert gravity.steam_url.startswith("https://store.steampowered.com/app/858710/")


def test_parse_free_games_ignores_non_100_discounts(settings: Settings) -> None:
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    games = parse_free_games(settings, html_content)

    assert all("123456" not in game.steam_url for game in games)


def test_parse_free_games_handles_malformed_rows(settings: Settings) -> None:
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    games = parse_free_games(settings, html_content)

    assert all(game.name for game in games)
    assert all(game.steam_url.startswith("https://store.steampowered.com/app/") for game in games)


def test_parse_free_games_empty_table(settings: Settings) -> None:
    html = (
        '<html><body><table class="table-sales table-hover table-sortable">'
        "<tbody></tbody></table></body></html>"
    )
    assert parse_free_games(settings, html) == []
