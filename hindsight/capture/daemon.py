"""Hindsight capture daemon.

Polls the foreground window and clipboard, applies privacy filters, and
streams events into Supermemory Local. Periodically syncs browser history.

Run with:  python -m hindsight.capture
"""

from __future__ import annotations

import signal
import sys
import threading
import time

from ..config import CONFIG
from ..sm_client import SupermemoryClient
from ..state import get_state, is_excluded
from . import privacy
from .clipboard import ClipboardWatcher
from .ingest import Event, Ingestor
from .window import get_foreground_window


class CaptureDaemon:
    def __init__(self) -> None:
        cap = CONFIG["capture"]
        self.poll_interval = float(cap["poll_interval_seconds"])
        self.min_focus = float(cap["min_focus_seconds"])
        self.do_clipboard = bool(cap["clipboard"])
        self.do_windows = bool(cap["windows"])
        self.do_browser = bool(cap["browser_history"])
        self.browser_sync = float(cap["browser_sync_minutes"]) * 60
        self.do_ocr = bool(cap.get("ocr", False))
        self.ocr_min_interval = float(cap.get("ocr_min_interval_seconds", 20))

        self.client = SupermemoryClient()
        self.ingestor = Ingestor(self.client, float(cap["batch_flush_seconds"]))
        self.clipboard = ClipboardWatcher()

        self._paused = False
        self._running = True
        self._last_window_key: str | None = None
        self._window_since = 0.0
        self._window_committed = False
        self._last_browser_sync = 0.0
        self._last_ocr = 0.0
        self._ocr_busy = False
        self._srcs: dict = {}

    # -- lifecycle ---------------------------------------------------------
    def run(self) -> None:
        if not self.client.ping():
            print(
                "[hindsight] cannot reach Supermemory Local at "
                f"{self.client.base_url}. Start it with scripts\\start_supermemory.ps1",
                file=sys.stderr,
            )
            sys.exit(1)

        self.ingestor.start()
        self._install_signal_handlers()
        print(f"[hindsight] capturing → {self.client.base_url} "
              f"(container: {self.client.container_tag})")
        print("[hindsight] Ctrl+C to stop. Send SIGBREAK to toggle pause.")

        try:
            while self._running:
                if not self._paused:
                    self._tick()
                time.sleep(self.poll_interval)
        finally:
            self.ingestor.stop()
            print(f"[hindsight] stopped. stored={self.ingestor.sent} "
                  f"failed={self.ingestor.failed}")

    def _tick(self) -> None:
        # Honour the runtime privacy state the app writes (pause + per-source
        # toggles). Read fresh each tick so changes take effect immediately.
        st = get_state()
        if st.get("paused"):
            return
        self._srcs = st.get("sources", {})
        now = time.monotonic()
        if self.do_windows and self._srcs.get("window", True):
            self._tick_window(now)
        if self.do_clipboard and self._srcs.get("clipboard", True):
            self._tick_clipboard()
        if (self.do_browser and self._srcs.get("browser", True)
                and (now - self._last_browser_sync) >= self.browser_sync):
            self._tick_browser()
            self._last_browser_sync = now

    # -- window ------------------------------------------------------------
    def _tick_window(self, now: float) -> None:
        win = get_foreground_window()
        key = f"{win.app}::{win.title}" if win else None

        if key != self._last_window_key:
            # Focus changed; start timing the new window.
            self._last_window_key = key
            self._window_since = now
            self._window_committed = False
            return

        if win is None or self._window_committed:
            return

        # Same window still focused — commit once it clears the dwell time.
        if (now - self._window_since) >= self.min_focus:
            self._window_committed = True
            if privacy.window_allowed(win.app, win.title) and not is_excluded(win.app, win.title):
                self.ingestor.submit(Event(
                    kind="window", content=win.title, source=win.app,
                    metadata={"app": win.app},
                ))
                if (self.do_ocr and self._srcs.get("ocr", True)
                        and (now - self._last_ocr) >= self.ocr_min_interval):
                    self._last_ocr = now
                    self._ocr_current_window(win)

    # -- ocr ---------------------------------------------------------------
    def _ocr_current_window(self, win) -> None:
        """OCR the screen on a background thread (it takes ~1-2s) so the poll
        loop keeps running. Only the recognized text is stored."""
        if self._ocr_busy:
            return
        self._ocr_busy = True

        def worker() -> None:
            try:
                from .ocr import ocr_screen
                res = ocr_screen()
                if res and privacy.clipboard_allowed(res.text):
                    self.ingestor.submit(Event(
                        kind="ocr", content=res.text, source=win.app,
                        metadata={"app": win.app, "window": win.title},
                    ))
            except Exception as exc:
                print(f"[hindsight] ocr failed: {exc}")
            finally:
                self._ocr_busy = False

        threading.Thread(target=worker, daemon=True).start()

    # -- clipboard ---------------------------------------------------------
    def _tick_clipboard(self) -> None:
        text = self.clipboard.poll()
        if text and privacy.clipboard_allowed(text) and not is_excluded(text):
            preview = text if len(text) <= 280 else text[:277] + "..."
            self.ingestor.submit(Event(kind="clipboard", content=preview))

    # -- browser -----------------------------------------------------------
    def _tick_browser(self) -> None:
        try:
            from .browser import sync_browser_history
        except Exception as exc:
            print(f"[hindsight] browser module unavailable: {exc}")
            return
        count = sync_browser_history(self.ingestor)
        if count:
            print(f"[hindsight] synced {count} browser visits")

    # -- control -----------------------------------------------------------
    def _toggle_pause(self, *_: object) -> None:
        self._paused = not self._paused
        print(f"[hindsight] {'PAUSED' if self._paused else 'RESUMED'} capture")

    def _stop(self, *_: object) -> None:
        self._running = False

    def _install_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)
        if hasattr(signal, "SIGBREAK"):  # Windows: Ctrl+Break toggles pause
            signal.signal(signal.SIGBREAK, self._toggle_pause)


def main() -> None:
    CaptureDaemon().run()


if __name__ == "__main__":
    main()
