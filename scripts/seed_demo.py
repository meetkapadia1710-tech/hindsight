"""Seed Supermemory Local with a realistic day of activity for demos.

    python scripts/seed_demo.py

Uses the same rich factual phrasing + entityContext as the live capture
daemon so the memory agent extracts grounded facts (not hallucinations).
The memory agent runs asynchronously; give it time to finish (watch the
container's memoryCount) before querying.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hindsight.capture.ingest import phrase_event  # noqa: E402
from hindsight.sm_client import SupermemoryClient  # noqa: E402

# (hours_ago, kind, raw_text, source)
SEED = [
    (7.0, "browser", "Understanding HNSW: the graph index behind fast vector search", "https://www.pinecone.io/learn/hnsw/"),
    (6.5, "window", "embeddings_notes.md - Visual Studio Code", "Code.exe"),
    (6.3, "clipboard", "cosine_similarity(a, b) = dot(a, b) / (norm(a) * norm(b))", "clipboard"),
    (5.9, "browser", "Supermemory self-hosting overview - one binary, runs on your machine", "https://supermemory.ai/docs/self-hosting/overview"),
    (5.5, "window", "Inbox (3) - Gmail - Google Chrome", "chrome.exe"),
    (5.2, "clipboard", "npx supermemory local", "clipboard"),
    (4.8, "browser", "WSL2 localhost forwarding explained", "https://learn.microsoft.com/windows/wsl/networking"),
    (3.6, "window", "hindsight - capture/daemon.py - Visual Studio Code", "Code.exe"),
    (3.1, "browser", "FastAPI in 5 minutes: building a tiny JSON API", "https://fastapi.tiangolo.com/"),
    (2.2, "browser", "How Microsoft Recall stores screenshots - Ars Technica", "firefox.exe"),
    (1.5, "browser", "Ollama: run large language models locally", "https://ollama.com/"),
    (0.8, "window", "Zoom Meeting - Supermemory hackathon office hours", "Zoom.exe"),
    (0.3, "clipboard", "forms.gle/ARXHNpFY5VNfiNDBA", "clipboard"),
]


def main() -> int:
    c = SupermemoryClient()
    if not c.ping():
        print("Supermemory Local not reachable on", c.base_url)
        return 1
    now = datetime.now(timezone.utc)
    batch = []
    for hours_ago, kind, raw, source in SEED:
        ts = (now - timedelta(hours=hours_ago)).isoformat()
        batch.append({
            "content": phrase_event(kind, raw, source, ts),
            "metadata": {"kind": kind, "source": source,
                         "captured_at": ts, "title": raw},
        })
        print(f"  + {kind:9} {raw[:58]}")
    c.add_memories(batch)
    print(f"\nSeeded {len(SEED)} memories directly (embedded locally, "
          "instantly searchable).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
