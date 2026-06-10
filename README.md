# steam-screip

Monitors [SteamDB sales](https://steamdb.info/sales) for 100% discounted games, stores new finds in TinyDB, and notifies via Discord webhook. Entries older than `RETENTION_DAYS` days are removed automatically.

## Setup

```bash
uv sync
cp .env.example .env
```

Set `DISCORD_WEBHOOK_URL` or `DISCORD_WEBHOOK_URLS` in `.env`. `DISCORD_WEBHOOK_URLS` accepts a comma- or newline-separated list of webhook URLs. All other settings have sensible defaults — see `.env.example` for parser XPaths, scraper headers, message template, and retention.

## Run

```bash
uv run steam-screip
```

#### Docker (Portainer):

- Create new stack
- Select build method as repository 
- Copy paste this repository link.
- Press `Load variables from .env file` button and select `.env.example` file
- Update variables according to your preferences
- Press `Deploy the stack`

