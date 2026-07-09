"""Privacy filters — decide what must never be captured.

This module is the trust boundary of Hindsight. If a window looks like a
password manager or a private browsing session, or a clipboard entry looks
like a secret, it is dropped before it ever reaches Supermemory.
"""

from __future__ import annotations

import re

from ..config import CONFIG

_priv = CONFIG["privacy"]
_excluded_procs = {p.lower() for p in _priv["excluded_processes"]}
_excluded_kw = [k.lower() for k in _priv["excluded_title_keywords"]]
_clip_deny = [re.compile(p, re.IGNORECASE) for p in _priv["clipboard_deny_patterns"]]
_max_clip = int(_priv["max_clipboard_chars"])


def window_allowed(app: str, title: str) -> bool:
    if app.lower() in _excluded_procs:
        return False
    hay = title.lower()
    return not any(kw in hay for kw in _excluded_kw)


def clipboard_allowed(text: str) -> bool:
    if len(text) > _max_clip:
        return False
    return not any(p.search(text) for p in _clip_deny)
