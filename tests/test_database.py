from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.database import game_exists, get_all_games, insert_game, open_database, purge_expired_games
from app.models import Game


@pytest.fixture
def sample_game() -> Game:
    return Game(
        name="Gravity Circuit",
        steam_url="https://store.steampowered.com/app/858710/",
        discovered_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def db(tmp_path: Path):
    database = open_database(str(tmp_path / "test_db.json"))
    yield database
    database.close()


def test_game_exists_by_steam_url(db, sample_game: Game) -> None:
    assert game_exists(db, sample_game) is False
    insert_game(db, sample_game)
    assert game_exists(db, sample_game) is True


def test_game_exists_by_app_id(db, sample_game: Game) -> None:
    insert_game(db, sample_game)

    variant = Game(
        name="Gravity Circuit (variant URL)",
        steam_url="https://store.steampowered.com/app/858710/?utm_source=test",
        discovered_at=datetime(2026, 1, 2, tzinfo=UTC),
    )
    assert game_exists(db, variant) is True


def test_insert_game_stores_app_id(db, sample_game: Game) -> None:
    insert_game(db, sample_game)
    records = get_all_games(db)
    assert len(records) == 1
    assert records[0]["app_id"] == "858710"
    assert records[0]["name"] == "Gravity Circuit"


def test_duplicate_insert_allowed_by_database_layer(db, sample_game: Game) -> None:
    insert_game(db, sample_game)
    insert_game(db, sample_game)
    assert len(get_all_games(db)) == 2


def test_purge_expired_games_removes_old_records(db, sample_game: Game) -> None:
    insert_game(db, sample_game)
    now = datetime(2026, 2, 1, tzinfo=UTC)

    removed = purge_expired_games(db, retention_days=30, now=now)

    assert removed == 1
    assert get_all_games(db) == []


def test_purge_expired_games_keeps_recent_records(db, sample_game: Game) -> None:
    insert_game(db, sample_game)
    now = datetime(2026, 1, 15, tzinfo=UTC)

    removed = purge_expired_games(db, retention_days=30, now=now)

    assert removed == 0
    assert len(get_all_games(db)) == 1


def test_purge_expired_games_disabled_when_retention_zero(db, sample_game: Game) -> None:
    insert_game(db, sample_game)
    now = datetime(2027, 1, 1, tzinfo=UTC)

    removed = purge_expired_games(db, retention_days=0, now=now)

    assert removed == 0
    assert len(get_all_games(db)) == 1
