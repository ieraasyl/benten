"""Telethon client for sending countdown messages (user bot)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)


def _env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "").strip()
    if required and not val:
        raise ValueError(f"{name} is required")
    return val


def new_client(gif_path: str | None = None) -> TelegramClient:
    api_id = int(_env("TELEGRAM_APP_ID"))
    api_hash = _env("TELEGRAM_APP_HASH")
    session_str = _env("TELEGRAM_SESSION").replace("\n", "").replace("\r", "")
    try:
        session = StringSession(session_str)
    except Exception as e:
        raise SystemExit(
            "Invalid TELEGRAM_SESSION (wrong format or corrupted).\n"
            "Session strings from the old Go version are not compatible.\n"
            "Generate a new one with: uv run python auth.py"
        ) from e
    client = TelegramClient(
        session,
        api_id,
        api_hash,
    )
    client._benten_gif_path = gif_path or ""
    return client


async def run(client: TelegramClient, targets: list[tuple[int, int]]) -> None:
    """Send countdown to each target. targets = [(user_id, number), ...]."""
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Not authorized: session may be invalid or expired")

    # Warm up peer cache so user IDs can be resolved (mirrors Go GetDialogs)
    try:
        await client.get_dialogs()
    except Exception as e:
        logger.warning("Could not fetch dialogs to warm peer cache: %s", e)

    gif_path: str = getattr(client, "_benten_gif_path", "") or ""

    for user_id, number in targets:
        try:
            await client.send_message(user_id, str(number))
            if number == 67 and gif_path:
                path = Path(gif_path)
                if path.is_file():
                    await client.send_file(user_id, str(path), caption="67")
                else:
                    logger.warning("GIF file not found: %s", gif_path)
        except Exception as e:
            logger.exception("Error sending to user %s: %s", user_id, e)
