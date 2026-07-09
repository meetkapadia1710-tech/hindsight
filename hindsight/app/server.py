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
    limit: int = 10


def _normalize_results(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a Supermemory search response into a list of memory dicts.

    Defensive about the exact response shape — different versions nest the
    hits under `results`, `documents`, or `memories`, and metadata may be a
    sibling of the content or embedded within it.
    """
    hits = (
        raw.get("results")
        or raw.get("documents")
        or raw.get("memories")
        or raw.get("data")
        or []
    )
    out: list[dict[str, Any]] = []
    for h in hits:
        if not isinstance(h, dict):
            continue
        meta = h.get("metadata") or {}
        content = (
            h.get("content")
            or h.get("text")
            or h.get("chunk")
            or h.get("memory")
            or ""
        )
        out.append({
            "content": content,
            "source": meta.get("source") or h.get("source") or "",
            "kind": meta.get("kind") or "",
            "captured_at": meta.get("captured_at") or h.get("createdAt") or "",
            "score": h.get("score") or h.get("similarity") or 0,
            "url": meta.get("url") or "",
        })
    return out


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": client.ping(), "base_url": client.base_url}


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
