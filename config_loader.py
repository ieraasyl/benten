"""Load and validate config.yaml for the countdown bot."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


@dataclass
class UserEntry:
    id: int


@dataclass
class Config:
    start_date: str
    users: list[UserEntry]
    timezone: str

    def parse_start_date(self) -> datetime:
        return datetime.strptime(self.start_date, "%Y-%m-%d").replace(
            tzinfo=ZoneInfo("UTC")
        )

    def location(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def load(path: str | Path) -> Config:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise ValueError("config is empty")
    if not data.get("start_date"):
        raise ValueError("start_date is required")
    if not data.get("users"):
        raise ValueError("at least one user is required")
    tz = data.get("timezone") or "Asia/Almaty"
    users = [UserEntry(id=u["id"]) for u in data["users"]]
    return Config(
        start_date=data["start_date"],
        users=users,
        timezone=tz,
    )
