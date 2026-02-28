"""Load and validate configuration from config.yaml and environment."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

DEFAULT_STORAGE_STATE_PATH = Path("playwright/storage_state.json")
DEFAULT_CONFIG_PATH = Path("config.yaml")


@dataclass
class NotificationConfig:
    """Optional notification settings."""

    email: dict[str, Any] = field(default_factory=dict)
    pushover: dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """Application configuration."""

    base_url: str
    restaurant: str
    dates: list[str]
    time_start: str | None
    time_end: str | None
    party_size: int
    auto_book: bool
    dry_run: bool
    poll_interval_minutes: int
    poll_jitter_seconds: int
    notifications: NotificationConfig
    storage_state_path: Path = DEFAULT_STORAGE_STATE_PATH

    @classmethod
    def load(cls, path: Path | str | None = None) -> Config:
        """Load config from YAML file. Uses config.yaml by default."""
        path = Path(path or DEFAULT_CONFIG_PATH)
        if not path.exists():
            raise FileNotFoundError(
                f"Config not found: {path}. Copy config.example.yaml to config.yaml and edit."
            )
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        notif = data.get("notifications") or {}
        email = notif.get("email") or {}
        pushover = notif.get("pushover") or {}
        # Allow env overrides for secrets
        if pushover.get("api_token") is None:
            pushover["api_token"] = os.environ.get("NOTIFY_PUSHOVER_TOKEN")
        if email.get("smtp_password") is None:
            email["smtp_password"] = os.environ.get("NOTIFY_SMTP_PASSWORD")

        return cls(
            base_url=(data.get("base_url") or "https://www.disneylandparis.com/en-gb").rstrip("/"),
            restaurant=data.get("restaurant") or "",
            dates=data.get("dates") or [],
            time_start=data.get("time_start") or None,
            time_end=data.get("time_end") or None,
            party_size=int(data.get("party_size") or 2),
            auto_book=bool(data.get("auto_book")),
            dry_run=bool(data.get("dry_run")),
            poll_interval_minutes=int(data.get("poll_interval_minutes") or 10),
            poll_jitter_seconds=int(data.get("poll_jitter_seconds") or 60),
            notifications=NotificationConfig(email=email, pushover=pushover),
            storage_state_path=Path(data.get("storage_state_path") or DEFAULT_STORAGE_STATE_PATH),
        )

    def validate(self) -> None:
        """Raise ValueError if required fields are missing."""
        if not self.restaurant:
            raise ValueError("config: 'restaurant' is required")
        if not self.dates:
            raise ValueError("config: 'dates' must contain at least one date (YYYY-MM-DD)")
