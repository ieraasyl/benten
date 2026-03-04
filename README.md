# Benten

A Python (Telethon) Telegram **user bot** that sends a daily countdown (100 down to 67) to a configurable list of users at a fixed time. When it sends 67, it also sends a "67 kid" GIF.

## Tech Stack

Python 3.13, [uv](https://docs.astral.sh/uv/), Telethon. Deployed via GitHub Actions (scheduled workflow). Uses a real Telegram account (MTProto), not the Bot API from @BotFather.

## Prerequisites

1. **Telegram API:** [my.telegram.org](https://my.telegram.org/) → API development tools → create app → get **App ID** and **App Hash**.
2. **67 kid GIF:** Add `assets/67kid.gif` to the repo (or set `GIF_PATH` when running locally).

## Setup

1. Clone the repo and `cd` into it.
2. Create `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
   Fill in `TELEGRAM_APP_ID`, `TELEGRAM_APP_HASH`, and `TELEGRAM_SESSION`.
3. Generate session string (one-time):
   ```bash
   uv run python auth.py
   ```
   Copy the printed `TELEGRAM_SESSION` into `.env`. **Never commit or share it**—it grants full access to your account.
4. Create `config.yaml` (see [config.example.yaml](config.example.yaml)):
   ```yaml
   start_date: "2026-12-25" # Day 0 = 100
   timezone: "Asia/Almaty"
   users:
     - id: 123456789
     - id: 987654321
   ```

## Development

```bash
uv run python main.py
```

Runs the countdown once (sends to all users based on today's date in the configured timezone).

**Test mode** (sends 100→67 to all users with a short delay between numbers):

```bash
BENTEN_TEST_INTERVAL_SECONDS=5 uv run python main.py
```

## Deploy

1. Push the repo to GitHub. Ensure `assets/67kid.gif` is committed.
2. Add repository secrets (Settings → Secrets and variables → Actions):
   - `TELEGRAM_APP_ID`
   - `TELEGRAM_APP_HASH`
   - `TELEGRAM_SESSION`
   - `CONFIG_YAML` — the **full contents** of your config file.
3. Edit [.github/workflows/daily-countdown.yml](.github/workflows/daily-countdown.yml) for schedule. Default cron is `0 6 * * *` (06:00 UTC = 12:00 Asia/Almaty). Use [crontab.guru](https://crontab.guru) to convert.
4. Run: Actions → "Daily countdown" → "Run workflow" to test immediately.

## Countdown Logic

- Day 0 (`start_date`): send 100.
- Day 1: 99, … Day 33: 67 + GIF.
- Day 34+: user is skipped (countdown finished).
- `timezone` (e.g. `Asia/Almaty`) defines when "today" changes.

## Useful Commands

- `uv run python main.py` — run countdown once
- `uv run python auth.py` — generate session string
- `BENTEN_TEST_INTERVAL_SECONDS=5 uv run python main.py` — test mode (sends all numbers with delay)
