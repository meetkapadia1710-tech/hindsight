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


def _try_ollama(question: str, context: str) -> str | None:
    prompt = (
        f"{SYSTEM_PROMPT}\n\nRetrieved memories:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    try:
        r = httpx.post(
            f"{_ans['ollama_url']}/api/generate",
            json={"model": _ans["ollama_model"], "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip() or None
    except (httpx.HTTPError, KeyError, ValueError):
        return None


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
    return (
        "Here's what I found in your history that seems most relevant "
        f"(no local LLM running, so this is a direct recall):\n\n{joined}"
    )


def _friendly_time(iso: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso)
        return dt.astimezone().strftime("%a %b %d, %I:%M %p")
    except (ValueError, TypeError):
        return iso or "unknown time"
