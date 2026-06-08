from loguru import logger
from lxml.html import HtmlElement, fromstring

from app.config import Settings
from app.models import Game


def _row_has_full_discount(row: HtmlElement, discount_xpath: str) -> bool:
    return bool(row.xpath(discount_xpath))


def _extract_name(row: HtmlElement, name_xpath: str) -> str | None:
    links = row.xpath(name_xpath)
    if not links:
        return None
    name = links[0].text_content().strip()
    return name or None


def _extract_steam_url(row: HtmlElement, store_xpath: str) -> str | None:
    links = row.xpath(store_xpath)
    if not links:
        return None
    url = links[0].get("href", "").strip()
    return url or None


def parse_free_games(settings: Settings, html_content: str) -> list[Game]:
    tree = fromstring(html_content)
    rows = tree.xpath(settings.parser_table_rows_xpath)

    games: list[Game] = []
    for row in rows:
        if not _row_has_full_discount(row, settings.parser_discount_xpath):
            continue

        name = _extract_name(row, settings.parser_name_xpath)
        steam_url = _extract_steam_url(row, settings.parser_store_xpath)

        if not name or not steam_url:
            logger.warning("Skipping malformed row: name={!r}, steam_url={!r}", name, steam_url)
            continue

        games.append(Game(name=name, steam_url=steam_url))

    logger.info("Parsed {} free game(s) with 100% discount", len(games))
    return games
