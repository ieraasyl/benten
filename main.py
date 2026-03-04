#!/usr/bin/env python3
"""Benten: daily countdown (100→67) via Telegram user bot. Sends number to configured users."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import dotenv

from bot_client import new_client, run
from config_loader import load

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config.yaml"
DEFAULT_GIF_PATH = "assets/67kid.gif"


def days_between(
    y1: int, m1: int, d1: int,
    y2: int, m2: int, d2: int,
) -> int:
    """Calendar days from (y1,m1,d1) to (y2,m2,d2). Positive means (y2,m2,d2) is after."""
    a = datetime(y1, m1, d1, tzinfo=timezone.utc)
    b = datetime(y2, m2, d2, tzinfo=timezone.utc)
    return (b - a).days


async def main_async() -> None:
    dotenv.load_dotenv()

    config_path = os.environ.get("CONFIG_PATH", "").strip() or DEFAULT_CONFIG_PATH
    gif_path = os.environ.get("GIF_PATH", "").strip() or DEFAULT_GIF_PATH

    cfg = load(config_path)
    interval_sec = os.environ.get("BENTEN_TEST_INTERVAL_SECONDS", "").strip()
    test_mode = interval_sec and interval_sec.isdigit() and int(interval_sec) > 0

    if test_mode:
        # Test mode: include all users, number is simulated day-by-day in the loop
        user_ids = [u.id for u in cfg.users]
        if not user_ids:
            logger.info("no users in config")
            return
        interval = int(interval_sec)
        logger.info(
            "TEST MODE: countdown 100→67 for %s user(s), every %s s (Ctrl+C to stop)",
            len(user_ids), interval,
        )
    else:
        loc = cfg.location()
        now = datetime.now(loc)
        today_y, today_m, today_d = now.year, now.month, now.day
        start_dt = cfg.parse_start_date()
        start_y, start_m, start_d = start_dt.year, start_dt.month, start_dt.day
        targets = []
        for u in cfg.users:
            days = days_between(start_y, start_m, start_d, today_y, today_m, today_d)
            if days < 0:
                logger.info(
                    "skipping user %s: start_date %s is in the future",
                    u.id, cfg.start_date,
                )
                continue
            if days > 33:
                logger.info("skipping user %s: countdown finished (day %s)", u.id, days)
                continue
            targets.append((u.id, 100 - days))
        if not targets:
            logger.info("no users to send to")
            return
        logger.info("sending to %s users (timezone: %s)", len(targets), cfg.timezone)

    client = new_client(gif_path)
    try:
        if test_mode:
            for day in range(34):
                number = 100 - day
                targets_this_round = [(uid, number) for uid in user_ids]
                await run(client, targets_this_round)
                logger.info("sent %s (day %s); next in %s s...", number, day, interval)
                if day < 33:
                    await asyncio.sleep(interval)
            logger.info("TEST MODE: countdown finished (100→67).")
        else:
            await run(client, targets)
            logger.info("done: sent to %s users", len(targets))
    finally:
        await client.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
