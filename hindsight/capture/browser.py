"""Browser history collector for Chromium-based browsers (Chrome, Edge, Brave).

Chromium keeps history in a SQLite file that is locked while the browser
runs, so we copy it to a temp file before reading. We remember the last
visit timestamp we ingested (per browser) to sync incrementally.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .ingest import Event, Ingestor
from . import privacy
from ..state import is_excluded

LOCAL = os.environ.get("LOCALAPPDATA", "")
# Chromium epoch: microseconds since 1601-01-01.
_CHROME_EPOCH_OFFSET = 11644473600_000_000

_BROWSERS: dict[str, Path] = {
    "Chrome": Path(LOCAL) / "Google/Chrome/User Data/Default/History",
    "Edge": Path(LOCAL) / "Microsoft/Edge/User Data/Default/History",
    "Brave": Path(LOCAL) / "BraveSoftware/Brave-Browser/User Data/Default/History",
}

# In-memory high-water mark per browser (Chromium visit time int).
_last_seen: dict[str, int] = {}
_STATE_FILE = Path(tempfile.gettempdir()) / "hindsight_browser_state.txt"


def _load_state() -> None:
    if _last_seen or not _STATE_FILE.exists():
        return
    for line in _STATE_FILE.read_text(encoding="utf-8").splitlines():
        name, _, val = line.partition("=")
        if val.isdigit():
            _last_seen[name] = int(val)


def _save_state() -> None:
    _STATE_FILE.write_text(
        "\n".join(f"{k}={v}" for k, v in _last_seen.items()), encoding="utf-8"
    )


def _chrome_time_to_iso(t: int) -> str:
    unix_us = t - _CHROME_EPOCH_OFFSET
    return datetime.fromtimestamp(unix_us / 1_000_000, tz=timezone.utc).isoformat()


def sync_browser_history(ingestor: Ingestor) -> int:
    """Ingest new visits since last sync. Returns number of visits ingested."""
    _load_state()
    total = 0
    for name, path in _BROWSERS.items():
        if not path.exists():
            continue
        total += _sync_one(name, path, ingestor)
    if total:
        _save_state()
    return total


def _sync_one(name: str, path: Path, ingestor: Ingestor) -> int:
    since = _last_seen.get(name, _default_since())
    tmp = Path(tempfile.gettempdir()) / f"hindsight_{name}_history.db"
    try:
        shutil.copy2(path, tmp)
    except OSError:
        return 0

    count = 0
    try:
        con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
        rows = con.execute(
            """
            SELECT urls.url, urls.title, visits.visit_time
            FROM visits JOIN urls ON urls.id = visits.url
            WHERE visits.visit_time > ?
            ORDER BY visits.visit_time ASC
            LIMIT 500
            """,
            (since,),
        ).fetchall()
        con.close()
    except sqlite3.Error:
        return 0
    finally:
        tmp.unlink(missing_ok=True)

    highest = since
    for url, title, visit_time in rows:
        highest = max(highest, visit_time)
        title = (title or "").strip()
        if not title or not privacy.window_allowed(name, title):
            continue
        if is_excluded(url, title):   # user's exclusion list (e.g. banking sites)
            continue
        ingestor.submit(Event(
            kind="browser",
            content=title,
            source=url,
            metadata={"browser": name, "url": url},
            ts=_chrome_time_to_iso(visit_time),
        ))
        count += 1

    if highest > since:
        _last_seen[name] = highest
    return count


def _default_since() -> int:
    """First run: only capture the last 24h so we don't dump all history."""
    unix_us = int((time.time() - 86400) * 1_000_000)
    return unix_us + _CHROME_EPOCH_OFFSET
