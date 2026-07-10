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

    def add_memory(
        self, content: str, metadata: dict[str, Any] | None = None,
    ) -> dict:
        """Insert one memory directly (skips the LLM extraction agent).

        Hindsight captures atomic activity events, so we store each one as a
        memory verbatim via /v4/memories rather than routing it through the
        document → memory-agent pipeline. That agent is slow (CPU-bound) and,
        with a small local model, either hallucinates or extracts nothing;
        direct insertion is instant, deterministic, and 100% accurate. The
        text is still embedded locally so it is semantically searchable.
        """
        return self.add_memories([{"content": content, "metadata": metadata or {}}])

    def add_memories(self, memories: list[dict[str, Any]]) -> dict:
        """Batch insert memories: [{content, metadata?, isStatic?}, ...]."""
        r = self._http.post(
            "/v4/memories",
            json={"containerTag": self.container_tag, "memories": memories},
        )
        r.raise_for_status()
        return r.json()

    def search(self, query: str, limit: int = 10, threshold: float = 0.4) -> dict:
        """Semantic search over stored memories via the v4 endpoint.

        (v3 search only covers raw document chunks and returns nothing for
        our directly-inserted memories in the local build.)
        """
        r = self._http.post(
            "/v4/search",
            json={
                "q": query,
                "containerTag": self.container_tag,
                "limit": limit,
                "threshold": threshold,
                "searchMode": "memories",
            },
        )
        r.raise_for_status()
        return r.json()

    def list_memories(
        self, limit: int = 50, order: str = "desc", sort: str = "createdAt",
    ) -> list[dict[str, Any]]:
        """Return raw memory entries for our container (newest-first by default).

        Used by the live feed (newest by insertion time), the daily digest, and
        the activity view. Sorting by `createdAt` means a freshly captured
        memory rises to the top the instant it is stored.
        """
        try:
            r = self._http.post(
                "/v4/memories/list",
                json={
                    "containerTags": [self.container_tag],
                    "limit": limit, "order": order, "sort": sort,
                },
            )
            r.raise_for_status()
            body = r.json()
            return body.get("memoryEntries", []) if isinstance(body, dict) else []
        except httpx.HTTPError:
            return []

    def stats(self) -> dict:
        """Return {memoryCount} for our container.

        Reads the total from /v4/memories/list pagination (the source of truth
        for directly inserted memories) without pulling every entry.
        """
        total = 0
        try:
            r = self._http.post(
                "/v4/memories/list",
                json={"containerTags": [self.container_tag], "limit": 1},
            )
            r.raise_for_status()
            body = r.json()
            total = (body.get("pagination", {}) or {}).get("totalItems", 0)
        except httpx.HTTPError:
            pass
        return {"memoryCount": total}

    def forget_one(self, memory_id: str) -> dict:
        """Delete a single memory by id."""
        r = self._http.request(
            "DELETE", "/v4/memories",
            json={"id": memory_id, "containerTag": self.container_tag},
        )
        r.raise_for_status()
        return r.json()

    def forget_all(self) -> dict:
        """Delete every memory in our container (the panic button)."""
        r = self._http.request(
            "DELETE", "/v3/documents/bulk",
            json={"containerTags": [self.container_tag]},
        )
        r.raise_for_status()
        return r.json()

    def ping(self) -> bool:
        try:
            r = self._http.get("/", timeout=3.0)
            return r.status_code < 500
        except httpx.HTTPError:
            return False
