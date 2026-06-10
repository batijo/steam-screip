import time

from loguru import logger
from tinydb import TinyDB

from app.config import Settings
from app.database import game_exists, insert_game, open_database, purge_expired_games
from app.logging_config import setup_logging
from app.notifier import NotifierError, send_game_notification
from app.parser import parse_free_games
from app.scraper import ScraperError, fetch_sales_page


def run_scrape(settings: Settings, db: TinyDB) -> None:
    logger.info("Starting scrape cycle")
    purge_expired_games(db, settings.retention_days)

    try:
        html_content = fetch_sales_page(settings)
    except (ScraperError, Exception) as exc:
        logger.error("Failed to fetch sales page: {}", exc)
        return

    try:
        games = parse_free_games(settings, html_content)
    except Exception as exc:
        logger.error("Failed to parse sales page: {}", exc)
        return

    new_games = [game for game in games if not game_exists(db, game)]
    logger.info("Found {} game(s), {} new", len(games), len(new_games))

    for game in new_games:
        if settings.all_discord_webhook_urls:
            try:
                send_game_notification(settings, game)
            except NotifierError as exc:
                logger.error("Discord notification failed for {}: {}", game.name, exc)
                continue
        else:
            logger.warning(
                "Discord webhook URL not configured; storing {} without notify",
                game.name,
            )

        try:
            insert_game(db, game)
        except Exception as exc:
            logger.error("Failed to insert {} into database: {}", game.name, exc)

    logger.info("Scrape cycle complete")


def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)

    logger.info("Starting steam-screip")
    logger.info("Scrape interval: {} seconds", settings.scrape_interval_seconds)
    logger.info("Database path: {}", settings.database_path)

    db = open_database(settings.database_path)

    while True:
        run_scrape(settings, db)
        logger.info("Sleeping for {} seconds", settings.scrape_interval_seconds)
        time.sleep(settings.scrape_interval_seconds)


if __name__ == "__main__":
    main()
