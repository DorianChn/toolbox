"""Configuration and paths for devcapsule.

All data lives under ~/.devcapsule/ by default (override with DEVCAPSULE_HOME).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

APP_NAME = "devcapsule"

# Settings keys exposed via `capsule config`. Each maps to an env-var override
# so a user can still override per-invocation without touching settings.json.
SETTING_KEYS = {
    "model": "DEVCAPSULE_MODEL",
    "extract_model": "DEVCAPSULE_EXTRACT_MODEL",
    "base_url": "DEVCAPSULE_BASE_URL",
    "embed_model": "DEVCAPSULE_EMBED_MODEL",
    "api_style": "DEVCAPSULE_API_STYLE",
    "api_key": "DEVCAPSULE_API_KEY",
}


def home_dir() -> Path:
    """Root data directory."""
    env = os.environ.get("DEVCAPSULE_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".devcapsule"


def db_path() -> Path:
    return home_dir() / "capsules.db"


def settings_path() -> Path:
    return home_dir() / "settings.json"


def ensure_home() -> Path:
    h = home_dir()
    h.mkdir(parents=True, exist_ok=True)
    return h


def load_settings() -> dict:
    """Read settings.json, returning {} if absent or invalid."""
    p = settings_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_settings(data: dict) -> None:
    ensure_home()
    settings_path().write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def get_setting(key: str) -> str | None:
    """Resolve a setting: env var wins, then settings.json, then None."""
    env = SETTING_KEYS.get(key)
    if env and os.environ.get(env):
        return os.environ[env]
    return load_settings().get(key)


def set_setting(key: str, value: str | None) -> None:
    data = load_settings()
    if value is None:
        data.pop(key, None)
    else:
        data[key] = value
    save_settings(data)
