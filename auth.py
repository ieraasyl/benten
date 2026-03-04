#!/usr/bin/env python3
"""Interactive login: prompts for phone/code, prints TELEGRAM_SESSION string for .env."""
from __future__ import annotations

import asyncio
import os

import dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

dotenv.load_dotenv()


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


async def main() -> None:
    api_id_str = _env("TELEGRAM_APP_ID")
    api_hash = _env("TELEGRAM_APP_HASH")

    if not api_id_str or not api_hash:
        print("App ID (from my.telegram.org): ", end="")
        api_id_str = input().strip()
        print("App Hash: ", end="")
        api_hash = input().strip()

    api_id = int(api_id_str)
    client = TelegramClient(StringSession(), api_id, api_hash)

    await client.start()
    session_string = client.session.save()

    print()
    print("=== TELEGRAM_SESSION (copy this to your env) ===")
    print(session_string)
    print("=== END ===")
    print()
    print("Set TELEGRAM_SESSION in your .env file.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
