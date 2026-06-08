from datetime import UTC, datetime, timedelta
from pathlib import Path

from loguru import logger
from tinydb import Query, TinyDB

from app.models import Game
from app.utils import extract_app_id

GameQuery = Query()


def _parse_discovered_at(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def open_database(path: str) -> TinyDB:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(str(db_path))


def game_exists(db: TinyDB, game: Game) -> bool:
    if db.search(GameQuery.steam_url == game.steam_url):
        return True

    app_id = extract_app_id(game.steam_url)
    if app_id and db.search(GameQuery.app_id == app_id):
        return True

    return False


def insert_game(db: TinyDB, game: Game) -> None:
    record = game.model_dump(mode="json")
    record["app_id"] = extract_app_id(game.steam_url)
    db.insert(record)
    logger.info("Inserted game into database: {}", game.name)


def get_all_games(db: TinyDB) -> list[dict]:
    return db.all()


def purge_expired_games(
    db: TinyDB,
    retention_days: int,
    *,
    now: datetime | None = None,
) -> int:
    if retention_days <= 0:
        return 0

    now = now or datetime.now(UTC)
    cutoff = now - timedelta(days=retention_days)
    removed = 0

    for record in db.all():
        discovered_at = record.get("discovered_at")
        if discovered_at is None:
            continue

        if _parse_discovered_at(discovered_at) < cutoff:
            db.remove(doc_ids=[record.doc_id])
            removed += 1

    if removed:
        logger.info("Purged {} game(s) older than {} days", removed, retention_days)

    return removed
