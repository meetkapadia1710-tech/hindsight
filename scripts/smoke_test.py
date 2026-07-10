"""End-to-end smoke test: add a memory to Supermemory Local, search it, then
clean it up so the demo container is left exactly as it was found.

    python scripts/smoke_test.py

Requires the server running on localhost:6767 and SUPERMEMORY_API_KEY set.
Exits non-zero if any step fails, so it doubles as a CI/health check.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hindsight.sm_client import SupermemoryClient  # noqa: E402


def main() -> int:
    c = SupermemoryClient()
    print(f"base_url = {c.base_url}")
    print(f"api_key set = {bool(c.api_key)}")
    if not c.ping():
        print("FAIL: cannot reach Supermemory Local")
        return 1
    print("ping = True")

    word = f"platypus-{int(time.time())}"
    marker = f"Hindsight smoke test — the secret word is {word}"
    print(f"\nAdding memory: {marker!r}")
    added = c.add_memory(marker, metadata={"kind": "window", "source": "smoke_test.py",
                                           "captured_at": "2026-07-10T00:00:00+00:00"})
    mem_id = (added.get("memories") or [{}])[0].get("id", "")
    print(f"added id = {mem_id}")

    print("\nWaiting for indexing…")
    time.sleep(3)

    print(f"Searching for '{word} secret word'…")
    res = c.search(f"{word} secret word", limit=5)
    hits = res.get("results", [])
    found = any(word in (h.get("memory") or "") for h in hits)
    print(f"search returned {len(hits)} results; marker found = {found}")

    if mem_id:
        c.forget_one(mem_id)
        print("cleaned up the throwaway memory")

    ok = found
    print("\nSMOKE TEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
