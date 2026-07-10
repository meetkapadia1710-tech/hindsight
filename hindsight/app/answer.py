"""Answer engine: turn retrieved memories into a grounded answer.

Tries a local Ollama model first so the whole thing works offline. If Ollama
isn't running, falls back to an extractive answer that just surfaces the most
relevant memories. Either way the UI shows the evidence timeline, so the user
can always verify.
"""

from __future__ import annotations

from typing import Any

import httpx

from ..config import CONFIG

_ans = CONFIG["answer"]


SYSTEM_PROMPT = (
    "You are Hindsight, a assistant that answers questions about the user's own "
    "computer activity using ONLY the retrieved memories provided. Each memory has "
    "a timestamp and a source (an app, a website, or the clipboard). Answer "
    "concisely and cite what you rely on by referring to the source and time. If "
    "the memories don't contain the answer, say so plainly — never invent activity."
)


def build_context(memories: list[dict[str, Any]]) -> str:
    lines = []
    for i, m in enumerate(memories, 1):
        ts = m.get("captured_at", "")
        src = m.get("source", "")
        content = m.get("content", "")   # accurate captured text
        lines.append(f"{i}. [{ts}] ({src}) {content}")
    return "\n".join(lines)


def answer_question(question: str, memories: list[dict[str, Any]]) -> dict[str, Any]:
    if not memories:
        return {
            "answer": "I don't have any memories matching that yet. Try rephrasing, "
                      "or give the capture daemon more time to observe.",
            "engine": "none",
        }

    context = build_context(memories)
    llm = _try_ollama(question, context)
    if llm is not None:
        return {"answer": llm, "engine": f"ollama:{_ans['ollama_model']}"}

    return {"answer": _extractive(question, memories), "engine": "extractive"}


def _ollama_generate(prompt: str, num_predict: int = 180) -> str | None:
    """One local Ollama generation, capped so the UI never hangs. Returns None
    on any failure so callers can fall back to an instant extractive result."""
    try:
        r = httpx.post(
            f"{_ans['ollama_url']}/api/generate",
            json={
                "model": _ans["ollama_model"],
                "prompt": prompt,
                "stream": False,
                "keep_alive": "30m",          # keep the model resident
                "options": {"num_predict": num_predict, "temperature": 0.2},
            },
            # Cap the wait: if the GPU is busy and the model is on CPU, we fall
            # back to an instant extractive result rather than making the user
            # wait tens of seconds.
            timeout=float(_ans.get("timeout_seconds", 12)),
        )
        r.raise_for_status()
        return r.json().get("response", "").strip() or None
    except (httpx.HTTPError, KeyError, ValueError):
        return None


def _try_ollama(question: str, context: str) -> str | None:
    prompt = (
        f"{SYSTEM_PROMPT}\n\nRetrieved memories:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    return _ollama_generate(prompt)


def _extractive(question: str, memories: list[dict[str, Any]]) -> str:
    top = memories[:5]
    bullets = []
    for m in top:
        ts = _friendly_time(m.get("captured_at", ""))
        src = m.get("source", "")
        content = m.get("content", "")
        src_str = f" — {src}" if src else ""
        bullets.append(f"• {ts}: {content}{src_str}")
    joined = "\n".join(bullets)
    return "Here's what I found in your history that matches:\n\n" + joined


def _friendly_time(iso: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso)
        return dt.astimezone().strftime("%a %b %d, %I:%M %p")
    except (ValueError, TypeError):
        return iso or "unknown time"


# -- daily digest ---------------------------------------------------------

DIGEST_PROMPT = (
    "You are Hindsight. Below are one user's own computer-activity records for a "
    "single day (each has a time, a source, and what they did). Write a warm, "
    "concise recap of their day as 5-8 bullet points, each starting with '- ', "
    "roughly ordered morning to evening, grouping related activity (topics "
    "researched, sites read, apps and files worked in, notable things copied). "
    "Use ONLY the facts below; never invent activity. Be specific and brief."
)


def _domain(url: str) -> str:
    from urllib.parse import urlparse
    try:
        h = urlparse(url).netloc
        return h[4:] if h.startswith("www.") else h
    except ValueError:
        return ""


def day_stats(memories: list[dict[str, Any]]) -> dict[str, Any]:
    from collections import Counter
    kinds: Counter = Counter()
    domains: Counter = Counter()
    apps: Counter = Counter()
    for m in memories:
        k = m.get("kind", "")
        kinds[k] += 1
        src = m.get("source", "")
        if k == "browser" and str(src).startswith("http"):
            d = _domain(src)
            if d:
                domains[d] += 1
        elif k == "window" and src:
            apps[src] += 1
    return {
        "total": len(memories),
        "kinds": dict(kinds),
        "top_domains": domains.most_common(5),
        "top_apps": apps.most_common(5),
    }


def summarize_day(memories: list[dict[str, Any]]) -> dict[str, Any]:
    """Return {summary, engine, stats} narrating a day's memories."""
    stats = day_stats(memories)
    if not memories:
        return {"summary": "No activity was recorded for that day.",
                "engine": "none", "stats": stats}

    # Order by capture time so the narrative reads morning -> evening.
    ordered = sorted(memories, key=lambda m: m.get("captured_at", ""))
    context = build_context(ordered[:40])
    llm = _ollama_generate(f"{DIGEST_PROMPT}\n\nRecords:\n{context}\n\nRecap:", num_predict=300)
    if llm is not None:
        return {"summary": llm, "engine": f"ollama:{_ans['ollama_model']}", "stats": stats}
    return {"summary": _extractive_digest(stats), "engine": "extractive", "stats": stats}


def _extractive_digest(stats: dict[str, Any]) -> str:
    lines = [f"You have {stats['total']} memories from this day:"]
    kinds = stats["kinds"]
    parts = []
    for label, key in [("pages visited", "browser"), ("windows used", "window"),
                       ("clipboard copies", "clipboard"), ("screen captures", "ocr")]:
        if kinds.get(key):
            parts.append(f"{kinds[key]} {label}")
    if parts:
        lines.append("- " + ", ".join(parts) + ".")
    if stats["top_domains"]:
        sites = ", ".join(f"{d} ({n})" for d, n in stats["top_domains"])
        lines.append(f"- Most-visited sites: {sites}.")
    if stats["top_apps"]:
        apps = ", ".join(f"{a} ({n})" for a, n in stats["top_apps"])
        lines.append(f"- Most-used apps: {apps}.")
    return "\n".join(lines)
