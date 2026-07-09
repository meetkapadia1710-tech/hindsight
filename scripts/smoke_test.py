"""End-to-end smoke test: add a memory to Supermemory Local, then search it.

    python scripts/smoke_test.py

Requires the server running on localhost:6767 and SUPERMEMORY_API_KEY set.
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
    print(f"ping = {c.ping()}")

    marker = f"Hindsight smoke test — the secret word is platypus-{int(time.time())}"
    print(f"\nAdding memory: {marker!r}")
    added = c.add(marker, metadata={"kind": "window", "source": "smoke_test.py",
                                    "captured_at": "2026-07-10T00:00:00+00:00"})
    print(f"add response: {added}")

    print("\nWaiting for indexing…")
    time.sleep(3)

    print("Searching for 'platypus secret word'…")
    res = c.search("platypus secret word", limit=5)
    print(f"search response: {res}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
