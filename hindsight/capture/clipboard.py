"""Clipboard text capture.

Uses GetClipboardSequenceNumber so we only open the clipboard when its
contents actually changed since the last poll.
"""

from __future__ import annotations

import ctypes

user32 = ctypes.windll.user32

try:
    import win32clipboard
    import win32con
except ImportError:  # pragma: no cover - non-Windows dev machines
    win32clipboard = None


class ClipboardWatcher:
    def __init__(self) -> None:
        # Start from the current state so we don't ingest whatever was
        # sitting in the clipboard before Hindsight started.
        self._last_seq = user32.GetClipboardSequenceNumber()
        self._last_text: str | None = None

    def poll(self) -> str | None:
        """Return new clipboard text, or None if unchanged/unavailable."""
        seq = user32.GetClipboardSequenceNumber()
        if seq == self._last_seq or win32clipboard is None:
            return None
        self._last_seq = seq

        text = self._read_text()
        if not text or text == self._last_text:
            return None
        self._last_text = text
        return text

    @staticmethod
    def _read_text() -> str | None:
        try:
            win32clipboard.OpenClipboard()
            try:
                if not win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    return None
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data.strip() if isinstance(data, str) else None
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            # Clipboard is a shared resource; another app may hold it open.
            return None
