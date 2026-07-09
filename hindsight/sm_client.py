"""Thin client for the Supermemory Local API (localhost:6767).

Same surface as the hosted v3 Memory API, pointed at the local server:
  POST /v3/documents  — add a memory
  POST /v3/search     — hybrid semantic search
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import CONFIG


class SupermemoryClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        sm = CONFIG["supermemory"]
        self.base_url = (base_url or sm["base_url"]).rstrip("/")
        self.api_key = api_key or sm["api_key"]
        self.container_tag = sm["container_tag"]
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    def add(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
        entity_context: str | None = None,
    ) -> dict:
        """Store one memory document."""
        payload: dict[str, Any] = {
            "content": content,
            "containerTag": self.container_tag,
        }
        if metadata:
            payload["metadata"] = metadata
        if entity_context:
            payload["entityContext"] = entity_context
        r = self._http.post("/v3/documents", json=payload)
        r.raise_for_status()
        return r.json()

    def search(self, query: str, limit: int = 10, threshold: float = 0.3) -> dict:
        """Hybrid semantic search over stored memories.

        Uses the v4 search endpoint (v3 search only covers raw chunks and
        returns nothing for agent-extracted memories in the local build).
        `searchMode: hybrid` searches both the LLM memories and the raw
        captured chunks; including documents + chunks lets us ground answers
        in the accurate captured text rather than the model's paraphrase.
        """
        r = self._http.post(
            "/v4/search",
            json={
                "q": query,
                "containerTag": self.container_tag,
                "limit": limit,
                "threshold": threshold,
                "searchMode": "hybrid",
                "include": {"documents": True, "chunks": True},
            },
        )
        r.raise_for_status()
        return r.json()

    def ping(self) -> bool:
        try:
            r = self._http.get("/", timeout=3.0)
            return r.status_code < 500
        except httpx.HTTPError:
            return False
