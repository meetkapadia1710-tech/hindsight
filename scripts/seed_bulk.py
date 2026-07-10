"""Seed a large, realistic month of activity (500+ memories) for demos.

    python scripts/seed_bulk.py [count]

Keeps the curated "anchor" memories from seed_demo (so the README example
queries still resolve) and fills the rest with varied browser / window /
clipboard events sampled across the last ~30 days. Everything is inserted
directly via Supermemory Local's /v4/memories and embedded on-device.
"""

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hindsight.capture.ingest import phrase_event  # noqa: E402
from hindsight.sm_client import SupermemoryClient  # noqa: E402
from seed_demo import SEED as ANCHORS  # noqa: E402

# --- content pools -------------------------------------------------------

ARTICLES = [
    ("Understanding HNSW: the graph index behind fast vector search", "https://www.pinecone.io/learn/hnsw/"),
    ("What are vector embeddings? A visual guide", "https://www.cloudflare.com/learning/ai/what-are-embeddings/"),
    ("How Microsoft Recall stores screenshots - Ars Technica", "https://arstechnica.com/recall-screenshots"),
    ("The case for local-first software", "https://www.inkandswitch.com/local-first/"),
    ("Retrieval-Augmented Generation explained", "https://huggingface.co/blog/rag"),
    ("SQLite: small, fast, reliable - pick any three", "https://www.sqlite.org/about.html"),
    ("Designing data-intensive applications: chapter 3 notes", "https://dataintensive.net/"),
    ("Why cosine similarity works for text embeddings", "https://www.pinecone.io/learn/cosine-similarity/"),
    ("HTTP caching for dummies", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching"),
    ("A visual introduction to machine learning", "http://www.r2d3.us/visual-intro-to-machine-learning-part-1/"),
    ("The Twelve-Factor App", "https://12factor.net/"),
    ("Rust ownership, borrowing, and lifetimes", "https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html"),
    ("How DNS works, in comic form", "https://howdns.works/"),
    ("Latency numbers every programmer should know", "https://gist.github.com/jboner/2841832"),
    ("Postgres full-text search vs. pgvector", "https://supabase.com/blog/pgvector"),
    ("Understanding async/await in Python", "https://realpython.com/async-io-python/"),
    ("The C4 model for software architecture", "https://c4model.com/"),
    ("Semantic search with sentence-transformers", "https://www.sbert.net/"),
    ("What every developer should know about time zones", "https://zachholman.com/talk/utc-is-enough-for-everyone-right"),
    ("Debugging: the 9 indispensable rules", "https://debuggingrules.com/"),
]
DOCS = [
    ("Supermemory self-hosting overview - one binary, runs on your machine", "https://supermemory.ai/docs/self-hosting/overview"),
    ("Supermemory quickstart: first memory in 2 minutes", "https://supermemory.ai/docs/self-hosting/quickstart"),
    ("Supermemory API reference - /v4/search", "https://supermemory.ai/docs/search"),
    ("Supermemory API reference - add memories", "https://supermemory.ai/docs/add-memories"),
    ("FastAPI in 5 minutes: building a tiny JSON API", "https://fastapi.tiangolo.com/"),
    ("Ollama: run large language models locally", "https://ollama.com/"),
    ("qwen2.5:3b - Ollama model library", "https://ollama.com/library/qwen2.5"),
    ("WSL2 localhost forwarding explained", "https://learn.microsoft.com/windows/wsl/networking"),
    ("uvicorn deployment settings", "https://www.uvicorn.org/settings/"),
    ("httpx: async HTTP client for Python", "https://www.python-httpx.org/"),
    ("Pydantic v2 model configuration", "https://docs.pydantic.dev/latest/"),
    ("Windows.Media.Ocr namespace reference", "https://learn.microsoft.com/uwp/api/windows.media.ocr"),
]
GITHUB = [
    "supermemoryai/supermemory", "ollama/ollama", "ggerganov/llama.cpp",
    "tiangolo/fastapi", "encode/httpx", "huggingface/transformers",
    "microsoft/WSL", "pallets/click", "psf/requests", "astral-sh/uv",
    "BerriAI/litellm", "chroma-core/chroma", "pgvector/pgvector",
]
YOUTUBE = [
    "lofi hip hop radio - beats to relax/study to", "Building a RAG app from scratch",
    "How vector databases work", "Rust in 100 seconds", "The Unreasonable Effectiveness of Embeddings",
    "WSL2 GPU passthrough setup", "Local LLMs on a laptop - full guide",
    "Designing a clean REST API", "SQLite the database everyone ignores",
    "3Blue1Brown - But what is a neural network?",
]
STACKOVERFLOW = [
    "pywin32 GetForegroundWindow returns 0", "asyncio.run cannot be called from a running loop",
    "read Chrome history sqlite while browser is open", "uvicorn address already in use 8787",
    "convert PIL Image to Windows SoftwareBitmap", "httpx.ConnectError connection refused localhost",
    "wsl2 cannot reach windows host from linux", "ollama model runs on CPU not GPU",
    "tomllib load config file python 3.13", "fastapi return HTMLResponse from string",
]
SHOPPING_NEWS = [
    ("Anker 737 Power Bank (24000mAh) - Amazon", "https://amazon.com/anker-737"),
    ("Mechanical keyboard switches compared - RTINGS", "https://rtings.com/keyboard/switches"),
    ("NVIDIA RTX 4050 laptop GPU review", "https://notebookcheck.net/rtx-4050"),
    ("Hacker News: Show HN: I built a local second brain", "https://news.ycombinator.com/"),
    ("The Verge: Windows 11 24H2 features", "https://theverge.com/windows-11-24h2"),
    ("RTX 4050 laptop GPU VRAM in WSL2 - Reddit", "https://reddit.com/r/ollama/wsl2-gpu"),
]

VSCODE_FILES = [
    "capture/daemon.py", "capture/ingest.py", "capture/window.py", "capture/clipboard.py",
    "capture/browser.py", "capture/ocr.py", "app/server.py", "app/ui.py", "app/answer.py",
    "sm_client.py", "config.py", "README.md", "SETUP.md", "requirements.txt",
    "embeddings_notes.md", "scratch/experiment.ipynb", "tests/test_search.py",
]
APPS = [
    ("Inbox (3) - Gmail - Google Chrome", "chrome.exe"),
    ("general - Supermemory - Discord", "Discord.exe"),
    ("#find-a-team - Discord", "Discord.exe"),
    ("Slack - hackathon", "slack.exe"),
    ("Notion - Hindsight planning", "Notion.exe"),
    ("Figma - Hindsight UI mockups", "Figma.exe"),
    ("Spotify - Deep Focus", "Spotify.exe"),
    ("Zoom Meeting - Supermemory hackathon office hours", "Zoom.exe"),
    ("Zoom Meeting - team standup", "Zoom.exe"),
    ("Task Manager", "Taskmgr.exe"),
]
TERMINALS = [
    "Windows PowerShell - ollama pull qwen2.5:3b",
    "Windows PowerShell - uvicorn hindsight.app.server:app",
    "Windows PowerShell - py -m hindsight.capture",
    "Ubuntu-24.04 - supermemory-server",
    "Windows PowerShell - git push origin main",
    "Windows PowerShell - pip install -r requirements.txt",
]
CLIP_SNIPPETS = [
    "npx supermemory local", "wsl --install -d Ubuntu-24.04 --no-launch",
    "ollama pull qwen2.5:3b-instruct", "git commit -m \"wip\"",
    "POST http://localhost:6767/v4/memories", "cosine_similarity(a, b) = dot(a, b) / (norm(a) * norm(b))",
    "SELECT url, title, visit_time FROM visits", "http://localhost:8787",
    "192.168.1.42", "forms.gle/ARXHNpFY5VNfiNDBA",
    "https://github.com/meetkapadia1710-tech/hindsight", "sk-REDACTED (do not paste secrets!)",
    "docker run -p 6767:6767 supermemory", "export OLLAMA_KEEP_ALIVE=30m",
    "curl -fsSL https://ollama.com/install.sh | sh", "pip install winrt-Windows.Media.Ocr",
]


def _gen_event(rng: random.Random):
    """Return (kind, raw_text, source) sampled from the pools."""
    r = rng.random()
    if r < 0.5:                      # browser (50%)
        cat = rng.choices(
            ["article", "docs", "github", "youtube", "so", "shop"],
            weights=[26, 20, 14, 12, 14, 14])[0]
        if cat == "article":
            t, u = rng.choice(ARTICLES); return "browser", t, u
        if cat == "docs":
            t, u = rng.choice(DOCS); return "browser", t, u
        if cat == "github":
            repo = rng.choice(GITHUB); return "browser", f"{repo} - GitHub", f"https://github.com/{repo}"
        if cat == "youtube":
            v = rng.choice(YOUTUBE); return "browser", f"{v} - YouTube", "https://youtube.com/watch"
        if cat == "so":
            q = rng.choice(STACKOVERFLOW); return "browser", f"{q} - Stack Overflow", "https://stackoverflow.com/questions"
        t, u = rng.choice(SHOPPING_NEWS); return "browser", t, u
    if r < 0.78:                     # window (28%)
        pick = rng.random()
        if pick < 0.45:
            f = rng.choice(VSCODE_FILES); return "window", f"hindsight - {f} - Visual Studio Code", "Code.exe"
        if pick < 0.70:
            t, a = rng.choice(APPS); return "window", t, a
        term = rng.choice(TERMINALS); return "window", term, "WindowsTerminal.exe"
    # clipboard (22%)
    return "clipboard", rng.choice(CLIP_SNIPPETS), "clipboard"


def _random_ts(rng: random.Random, days: int) -> str:
    now = datetime.now(timezone.utc)
    day = rng.randint(0, days - 1)
    # weight toward waking / working hours (8:00-24:00 local-ish)
    hour = rng.choices(range(0, 24), weights=(
        [1] * 8 + [5, 6, 7, 7, 6, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 2]))[0]
    minute = rng.randint(0, 59)
    ts = now - timedelta(days=day)
    ts = ts.replace(hour=hour, minute=minute, second=rng.randint(0, 59))
    return ts.isoformat()


def build(count: int, days: int = 30, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    memories: list[dict] = []
    now = datetime.now(timezone.utc)

    # anchors: the curated "today" set (keeps README example queries working)
    for hours_ago, kind, raw, source in ANCHORS:
        ts = (now - timedelta(hours=hours_ago)).isoformat()
        memories.append({
            "content": phrase_event(kind, raw, source, ts),
            "metadata": {"kind": kind, "source": source, "captured_at": ts, "title": raw},
        })

    # fill the rest with sampled history
    while len(memories) < count:
        kind, raw, source = _gen_event(rng)
        ts = _random_ts(rng, days)
        memories.append({
            "content": phrase_event(kind, raw, source, ts),
            "metadata": {"kind": kind, "source": source, "captured_at": ts, "title": raw},
        })
    return memories


def main() -> int:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 540
    c = SupermemoryClient()
    if not c.ping():
        print("Supermemory Local not reachable on", c.base_url)
        return 1

    print(f"Wiping container '{c.container_tag}'...")
    c.forget_all()

    mems = build(count)
    print(f"Inserting {len(mems)} memories in batches...")
    B = 100
    for i in range(0, len(mems), B):
        c.add_memories(mems[i:i + B])
        print(f"  inserted {min(i + B, len(mems))}/{len(mems)}")
    print(f"\nDone. Seeded {len(mems)} memories (embedded on-device).")
    print("Stats:", c.stats())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
