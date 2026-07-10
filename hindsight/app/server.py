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
from .answer import answer_question
from .ui import INDEX_HTML

app = FastAPI(title="Hindsight")
client = SupermemoryClient()


class AskRequest(BaseModel):
    question: str
    limit: int = 6


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


@app.post("/api/ask")
def ask(req: AskRequest) -> JSONResponse:
    try:
        raw = client.search(req.question, limit=req.limit)
    except Exception as exc:
        return JSONResponse(
            {"error": f"search failed: {exc}", "answer": "", "evidence": []},
            status_code=502,
        )
    memories = _normalize_results(raw)
    result = answer_question(req.question, memories)
    return JSONResponse({
        "answer": result["answer"],
        "engine": result["engine"],
        "evidence": memories,
    })


def main() -> None:
    import uvicorn

    a = CONFIG["app"]
    print(f"[hindsight] query app → http://{a['host']}:{a['port']}")
    uvicorn.run(app, host=a["host"], port=int(a["port"]), log_level="warning")


if __name__ == "__main__":
    main()
