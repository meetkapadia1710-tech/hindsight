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

# (hours_ago, kind, raw_text, source) — a believable full day of activity.
SEED = [
    # --- early morning: research ---
    (9.5, "browser", "Understanding HNSW: the graph index behind fast vector search", "https://www.pinecone.io/learn/hnsw/"),
    (9.3, "browser", "bge-base-en-v1.5 embedding model card", "https://huggingface.co/BAAI/bge-base-en-v1.5"),
    (9.1, "clipboard", "cosine_similarity(a, b) = dot(a, b) / (norm(a) * norm(b))", "clipboard"),
    (8.8, "window", "embeddings_notes.md - Visual Studio Code", "Code.exe"),
    (8.5, "browser", "Supermemory self-hosting overview - one binary, runs on your machine", "https://supermemory.ai/docs/self-hosting/overview"),
    (8.2, "clipboard", "npx supermemory local", "clipboard"),
    # --- email + planning ---
    (7.7, "window", "Inbox (3) - Gmail - Google Chrome", "chrome.exe"),
    (7.5, "browser", "Localhost:6767 hackathon - rules and prizes", "https://supermemory.ai/hackathon"),
    (7.2, "clipboard", "forms.gle/ARXHNpFY5VNfiNDBA", "clipboard"),
    # --- setup / infra ---
    (6.6, "browser", "WSL2 localhost forwarding explained", "https://learn.microsoft.com/windows/wsl/networking"),
    (6.3, "browser", "Ollama: run large language models locally", "https://ollama.com/"),
    (6.0, "clipboard", "wsl --install -d Ubuntu-24.04 --no-launch", "clipboard"),
    (5.7, "window", "Windows PowerShell - ollama pull qwen2.5:3b", "WindowsTerminal.exe"),
    (5.4, "browser", "qwen2.5:3b - Ollama model library", "https://ollama.com/library/qwen2.5"),
    # --- building ---
    (4.9, "window", "hindsight - capture/daemon.py - Visual Studio Code", "Code.exe"),
    (4.6, "browser", "FastAPI in 5 minutes: building a tiny JSON API", "https://fastapi.tiangolo.com/"),
    (4.3, "browser", "pywin32 GetForegroundWindow example - Stack Overflow", "https://stackoverflow.com/questions/pywin32-foreground-window"),
    (4.0, "clipboard", "git commit -m \"Scaffold Hindsight\"", "clipboard"),
    (3.7, "window", "hindsight - app/ui.py - Visual Studio Code", "Code.exe"),
    (3.4, "browser", "supermemoryai/supermemory - GitHub", "https://github.com/supermemoryai/supermemory"),
    # --- a break ---
    (3.0, "browser", "How Microsoft Recall stores screenshots - Ars Technica", "firefox.exe"),
    (2.7, "browser", "lofi hip hop radio - beats to relax/study to - YouTube", "https://youtube.com/watch?v=jfKfPfyJRdk"),
    (2.4, "clipboard", "192.168.1.42", "clipboard"),
    # --- afternoon: debugging + docs ---
    (2.0, "window", "Windows PowerShell - uvicorn hindsight.app.server:app", "WindowsTerminal.exe"),
    (1.7, "browser", "Supermemory API reference - /v4/search", "https://supermemory.ai/docs/search"),
    (1.4, "clipboard", "POST http://localhost:6767/v4/memories", "clipboard"),
    (1.1, "browser", "RTX 4050 laptop GPU VRAM in WSL2 - Reddit", "https://reddit.com/r/ollama/wsl2-gpu"),
    # --- wrap-up ---
    (0.7, "window", "Zoom Meeting - Supermemory hackathon office hours", "Zoom.exe"),
    (0.4, "window", "hindsight - README.md - Visual Studio Code", "Code.exe"),
    (0.2, "clipboard", "https://github.com/meetkapadia1710-tech/hindsight", "clipboard"),
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
