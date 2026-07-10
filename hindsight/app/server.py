"""Hindsight query app — FastAPI server + single-page UI.

Run with:  python -m hindsight.app
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from ..config import CONFIG
from ..sm_client import SupermemoryClient
from .. import state as runtime_state
from .answer import answer_question, summarize_day
from .ui import INDEX_HTML

app = FastAPI(title="Hindsight")
client = SupermemoryClient()


class AskRequest(BaseModel):
    question: str
    limit: int = 6
    scope: str = "all"   # all | today | yesterday | week


def _scope_bounds(scope: str):
    """Return (start, end) datetimes in local time for a named time scope, or
    None for 'all'. Used to answer time-scoped questions."""
    from datetime import datetime, timedelta
    now = datetime.now().astimezone()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if scope == "today":
        return midnight, now
    if scope == "yesterday":
        return midnight - timedelta(days=1), midnight
    if scope == "week":
        return now - timedelta(days=7), now
    return None


def _within(iso: str, bounds) -> bool:
    if not bounds:
        return True
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso).astimezone()
    except (ValueError, TypeError):
        return False
    return bounds[0] <= dt <= bounds[1]


def _clean(text: str) -> str:
    """Strip the '[Kind] ... (source: ...)' wrapper we add at capture time so
    the UI shows just the human-readable activity."""
    import re
    text = re.sub(r"^\[[^\]]+\]\s*", "", text or "")
    text = re.sub(r"\s*\(source:[^)]*\)\s*$", "", text)
    return text.strip()


def _normalize_results(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a v4 hybrid-search response into memory dicts for the UI.

    Each v4 result carries the model's `memory` plus the accurate captured
    text under `chunks[].content` / `documents[].title`. We surface the
    accurate text as `content` (grounding), keep `memory` as a secondary
    interpretation, and pull source/kind/time from the metadata we stored.
    """
    hits = raw.get("results") or raw.get("data") or []
    out: list[dict[str, Any]] = []
    seen: dict[str, int] = {}   # dedup key -> index in out
    for h in hits:
        if not isinstance(h, dict):
            continue
        meta = h.get("metadata") or {}
        chunks = h.get("chunks") or []
        docs = h.get("documents") or []
        # Prefer the exact captured text we stored; fall back to chunk/title.
        accurate = meta.get("title") or ""
        if not accurate and chunks and isinstance(chunks[0], dict):
            accurate = _clean(chunks[0].get("content") or "")
        if not accurate and docs and isinstance(docs[0], dict):
            accurate = _clean(docs[0].get("title") or "")
        memory = h.get("memory") or ""
        source = meta.get("source") or ""
        content = accurate or _clean(memory)
        score = round(float(h.get("similarity") or h.get("score") or 0), 3)

        key = f"{content}::{source}".lower()
        if key in seen:  # collapse duplicate memories from the same event
            if score > out[seen[key]]["score"]:
                out[seen[key]]["score"] = score
            continue
        seen[key] = len(out)
        out.append({
            "id": h.get("id") or h.get("rootMemoryId") or "",
            "content": content,
            "memory": memory,
            "source": source,
            "kind": meta.get("kind") or "",
            "captured_at": meta.get("captured_at") or h.get("updatedAt") or "",
            "score": score,
            "url": source if str(source).startswith("http") else "",
        })
    return out


def _entry_to_memory(entry: dict[str, Any]) -> dict[str, Any]:
    """Normalize a /v4/memories/list entry into the UI's memory shape."""
    meta = entry.get("metadata") or {}
    source = meta.get("source") or ""
    content = meta.get("title") or _clean(entry.get("memory") or "")
    return {
        "id": entry.get("id") or "",
        "content": content,
        "memory": entry.get("memory") or "",
        "source": source,
        "kind": meta.get("kind") or "",
        "captured_at": meta.get("captured_at") or entry.get("createdAt") or "",
        "created_at": entry.get("createdAt") or "",
        "url": source if str(source).startswith("http") else "",
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": client.ping(), "base_url": client.base_url}


@app.get("/api/stats")
def stats() -> dict[str, Any]:
    return client.stats()


@app.get("/api/recent")
def recent(limit: int = 10) -> JSONResponse:
    """Newest memories by insertion time — powers the live capture feed."""
    limit = max(1, min(limit, 50))
    entries = client.list_memories(limit=limit, order="desc", sort="createdAt")
    return JSONResponse({"memories": [_entry_to_memory(e) for e in entries]})


@app.post("/api/forget_all")
def forget_all() -> JSONResponse:
    try:
        return JSONResponse(client.forget_all())
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)


class ForgetOneRequest(BaseModel):
    id: str


@app.post("/api/forget_one")
def forget_one(req: ForgetOneRequest) -> JSONResponse:
    if not req.id:
        return JSONResponse({"error": "missing id"}, status_code=400)
    try:
        return JSONResponse(client.forget_one(req.id))
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)


class SettingsPatch(BaseModel):
    paused: bool | None = None
    sources: dict[str, bool] | None = None
    exclusions: list[str] | None = None


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
    """Current privacy/capture state (shared with the daemon via a state file)."""
    return runtime_state.get_state()


@app.post("/api/settings")
def set_settings(patch: SettingsPatch) -> JSONResponse:
    return JSONResponse(runtime_state.update_state(patch.model_dump(exclude_none=True)))


class DigestRequest(BaseModel):
    date: str = ""   # YYYY-MM-DD, defaults to today (local)


@app.post("/api/digest")
def digest(req: DigestRequest) -> JSONResponse:
    """Narrate one day's activity, grouped and summarized, with the memories
    behind it as evidence."""
    from datetime import datetime, timedelta
    now = datetime.now().astimezone()
    try:
        base = datetime.fromisoformat(req.date).astimezone() if req.date else now
    except ValueError:
        base = now
    start = base.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    entries = client.list_memories(limit=1000, order="desc", sort="createdAt")
    day = [m for m in (_entry_to_memory(e) for e in entries)
           if _within(m["captured_at"], (start, end))]
    result = summarize_day(day)
    day_sorted = sorted(day, key=lambda m: m["captured_at"], reverse=True)
    return JSONResponse({
        "answer": result["summary"],
        "engine": result["engine"],
        "evidence": day_sorted[:8],
        "scope": "digest",
        "date": start.strftime("%A, %B %d"),
        "stats": result["stats"],
    })


@app.post("/api/ask")
def ask(req: AskRequest) -> JSONResponse:
    question = (req.question or "").strip()
    if not question:
        return JSONResponse({"answer": "Ask a question to search your memory.",
                             "engine": "none", "evidence": [], "scope": "all"})
    limit = max(1, min(req.limit or 6, 20))   # clamp so odd inputs can't over-query
    scope = (req.scope or "all").lower()
    bounds = _scope_bounds(scope)
    # Pull a wide candidate set, then (for a time scope) filter by capture time
    # before answering, so narrowing the window never yields *more* results
    # than "all time" and the window doesn't starve. Capped at 100 — the max
    # Supermemory /v4/search accepts.
    search_limit = min(max(limit * 6, 40), 100)
    try:
        raw = client.search(question, limit=search_limit)
    except Exception as exc:
        return JSONResponse(
            {"error": f"search failed: {exc}", "answer": "", "evidence": []},
            status_code=502,
        )
    memories = _normalize_results(raw)
    if bounds:
        memories = [m for m in memories if _within(m["captured_at"], bounds)]
    memories = memories[:limit]
    result = answer_question(question, memories)
    return JSONResponse({
        "answer": result["answer"],
        "engine": result["engine"],
        "evidence": memories,
        "scope": scope,
    })


def main() -> None:
    import uvicorn

    a = CONFIG["app"]
    print(f"[hindsight] query app → http://{a['host']}:{a['port']}")
    uvicorn.run(app, host=a["host"], port=int(a["port"]), log_level="warning")


if __name__ == "__main__":
    main()
