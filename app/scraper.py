from curl_cffi import requests
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings


class ScraperError(Exception):
    pass


def _build_headers(settings: Settings) -> dict[str, str]:
    return {
        "Accept": settings.scrape_accept,
        "Accept-Language": settings.scrape_accept_language,
        "Accept-Encoding": settings.scrape_accept_encoding,
        "User-Agent": settings.scrape_user_agent,
    }


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((ScraperError, requests.RequestsError)),
)
def fetch_sales_page(settings: Settings) -> str:
    logger.info("Fetching SteamDB sales page: {}", settings.steamdb_sales_url)

    try:
        response = requests.get(
            settings.steamdb_sales_url,
            headers=_build_headers(settings),
            impersonate=settings.scrape_impersonate,
            timeout=settings.scrape_timeout_seconds,
        )
    except requests.RequestsError as exc:
        logger.error("Network error while fetching sales page: {}", exc)
        raise

    if response.status_code != 200:
        logger.error("Unexpected HTTP status {} from SteamDB", response.status_code)
        raise ScraperError(f"SteamDB returned HTTP {response.status_code}")

    logger.info("Successfully fetched sales page ({} bytes)", len(response.text))
    return response.text
