import re

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    discord_webhook_url: str = ""
    discord_webhook_urls: list[str] = []
    database_path: str = "data/db.json"
    scrape_interval_seconds: int = 300
    log_level: str = "INFO"
    discord_username: str = "Steam Free Games"
    discord_avatar_url: str = ""
    discord_message_template: str = "🎮 New Free Steam Game\n\n{name}\n{steam_url}"
    steamdb_sales_url: str = "https://steamdb.info/sales/?sort=discount_desc"

    @field_validator("discord_webhook_urls", mode="before")
    @classmethod
    def _parse_discord_webhook_urls(cls, value):
        if isinstance(value, str):
            return [url.strip() for url in re.split(r"[\n\r,]+", value) if url.strip()]
        return value

    @property
    def all_discord_webhook_urls(self) -> list[str]:
        urls: list[str] = []
        if self.discord_webhook_url:
            urls.append(self.discord_webhook_url.strip())
        for url in self.discord_webhook_urls:
            if url and url.strip():
                urls.append(url.strip())

        deduped: list[str] = []
        seen: set[str] = set()
        for url in urls:
            if url not in seen:
                seen.add(url)
                deduped.append(url)
        return deduped

    scrape_user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:150.0) Gecko/20100101 Firefox/150.0"
    )
    scrape_accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    scrape_accept_language: str = "en-US,en;q=0.9"
    scrape_accept_encoding: str = "gzip, deflate, br"
    scrape_impersonate: str = "firefox"
    scrape_timeout_seconds: int = 30

    parser_table_rows_xpath: str = "//table[contains(@class, 'table-sales')]//tbody/tr"
    parser_discount_xpath: str = (
        ".//td[contains(@class, 'price-discount') and @data-sort='100']"
    )
    parser_name_xpath: str = ".//a[contains(@class, 'b') and contains(@href, '/app/')]"
    parser_store_xpath: str = (
        ".//a[contains(@class, 'info-icon') and contains(@href, 'store.steampowered.com')]"
    )

    retention_days: int = 30
