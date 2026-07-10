"""Shared runtime state between the capture daemon and the query app.

The two run as separate processes, so they coordinate through a small JSON
file (``.hindsight/state.json`` at the repo root, gitignored). The app writes
it from the privacy controls; the daemon reads it each poll and honours it:

    {
      "paused": false,
      "sources": {"browser": true, "window": true, "clipboard": true, "ocr": false},
      "exclusions": ["chase.com", "1password"]
    }
"""

from __future__ import annotations

import json
from typing import Any

from .config import ROOT

STATE_DIR = ROOT / ".hindsight"
STATE_FILE = STATE_DIR / "state.json"

DEFAULTS: dict[str, Any] = {
    "paused": False,
    "sources": {"browser": True, "window": True, "clipboard": True, "ocr": False},
    "exclusions": [],
}


def get_state() -> dict[str, Any]:
    """Return the current state, with defaults filled in for missing keys."""
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    state = {**DEFAULTS, **data}
    state["sources"] = {**DEFAULTS["sources"], **(data.get("sources") or {})}
    excl = data.get("exclusions") or []
    state["exclusions"] = [str(x) for x in excl if str(x).strip()]
    return state


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def update_state(patch: dict[str, Any]) -> dict[str, Any]:
    """Merge a partial update into the state and persist it."""
    state = get_state()
    if "paused" in patch:
        state["paused"] = bool(patch["paused"])
    if isinstance(patch.get("sources"), dict):
        state["sources"].update({k: bool(v) for k, v in patch["sources"].items()})
    if isinstance(patch.get("exclusions"), list):
        state["exclusions"] = [str(x) for x in patch["exclusions"] if str(x).strip()]
    return save_state(state)


def is_excluded(*fields: str) -> bool:
    """True if any exclusion term appears in the given text fields (source,
    window title, url, clipboard text). Case-insensitive substring match."""
    hay = " ".join(f for f in fields if f).lower()
    if not hay:
        return False
    return any(term.lower() in hay for term in get_state().get("exclusions", []))
