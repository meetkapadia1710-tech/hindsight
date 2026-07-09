"""Foreground window tracking via win32 (ctypes, no extra deps)."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

import psutil

user32 = ctypes.windll.user32


@dataclass(frozen=True)
class ForegroundWindow:
    app: str      # process executable name, e.g. "chrome.exe"
    title: str    # window title text


def get_foreground_window() -> ForegroundWindow | None:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None

    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value.strip()

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        app = psutil.Process(pid.value).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        app = "unknown"

    if not title:
        return None
    return ForegroundWindow(app=app, title=title)
