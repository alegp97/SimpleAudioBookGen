"""Filesystem paths used by the application."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "SimpleAudioBookGen"


def is_frozen() -> bool:
    """Return whether the app is running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


def user_data_dir() -> Path:
    """Return a per-user writable directory for settings and diagnostics."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_NAME

    return Path.home() / f".{APP_NAME.lower()}"


def ensure_user_data_dir() -> Path:
    """Create and return the writable app data directory."""
    path = user_data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path
