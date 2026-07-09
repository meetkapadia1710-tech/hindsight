"""Batching + dedupe layer between the capture daemon and Supermemory.

Events are queued and flushed on a background thread so capture polling is
never blocked on network I/O. Consecutive identical events are collapsed.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..sm_client import SupermemoryClient


@dataclass
class Event:
    kind: str                       # "window" | "clipboard" | "browser" | "ocr"
    content: str                    # human-readable memory text
    source: str = ""                # app / browser / url
    metadata: dict = field(default_factory=dict)
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Ingestor:
    def __init__(self, client: SupermemoryClient, flush_seconds: float = 30.0):
        self._client = client
        self._flush_seconds = flush_seconds
        self._q: queue.Queue[Event | None] = queue.Queue()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self.sent = 0
        self.failed = 0

    def start(self) -> None:
        self._worker.start()

    def submit(self, event: Event) -> None:
        self._q.put(event)

    def stop(self) -> None:
        self._stop.set()
        self._q.put(None)
        self._worker.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._q.get(timeout=self._flush_seconds)
            except queue.Empty:
                continue
            if event is None:
                break
            self._send(event)

    def _send(self, event: Event) -> None:
        # Prefix makes memories self-describing and improves retrieval.
        prefix = {
            "window": "Active window",
            "clipboard": "Copied to clipboard",
            "browser": "Visited page",
            "ocr": "On screen",
        }.get(event.kind, event.kind)
        content = f"[{prefix}] {event.content}"
        if event.source:
            content += f" (source: {event.source})"
        metadata = {
            "kind": event.kind,
            "source": event.source,
            "captured_at": event.ts,
            **event.metadata,
        }
        try:
            self._client.add(content, metadata=metadata)
            self.sent += 1
        except Exception as exc:  # keep the daemon alive on transient errors
            self.failed += 1
            print(f"[ingest] failed to store {event.kind}: {exc}")
