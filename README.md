# steam-screip

Monitors [SteamDB sales](https://steamdb.info/sales) for 100% discounted games, stores new finds in TinyDB, and notifies via Discord webhook. Entries older than `RETENTION_DAYS` days are removed automatically.

## Setup

```bash
uv sync
cp .env.example .env
```

Set `DISCORD_WEBHOOK_URL` in `.env`. All other settings have sensible defaults — see `.env.example` for parser XPaths, scraper headers, message template, and retention.

## Run

```bash
uv run steam-screip
```

Docker:

```bash
docker compose up -d
```
