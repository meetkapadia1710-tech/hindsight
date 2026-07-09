"""Configuration loading for Hindsight.

Reads config.toml from the repo root and the Supermemory API key from the
SUPERMEMORY_API_KEY environment variable or a .env file next to config.toml.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.toml"
ENV_PATH = ROOT / ".env"


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "rb") as f:
        cfg = tomllib.load(f)
    _load_dotenv(ENV_PATH)
    cfg["supermemory"]["api_key"] = os.environ.get("SUPERMEMORY_API_KEY", "")
    return cfg


CONFIG = load_config()
