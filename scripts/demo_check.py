"""Verify the scripted demo queries still return their expected evidence, and
that time-scoping is correct — run this right before recording.

    python scripts/demo_check.py

Non-destructive. Hits the running app at 127.0.0.1:8787.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

BASE = "http://127.0.0.1:8787"
_fail = 0


def post(path, body, timeout=40):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    t = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()), (time.time() - t) * 1000


def anchor(question, expect_kw, scope="all"):
    global _fail
    j, ms = post("/api/ask", {"question": question, "scope": scope})
    ev = j.get("evidence", [])
    blob = " ".join((e.get("content", "") + " " + e.get("source", "")) for e in ev).lower()
    hit = expect_kw.lower() in blob
    print(f"  [{'PASS' if hit else 'FAIL'}] {question!r} (scope={scope}) -> "
          f"{len(ev)} ev, engine={j.get('engine')}, {ms:.0f}ms; expected '{expect_kw}' {'found' if hit else 'MISSING'}")
    if not hit:
        _fail += 1
    return j


def main() -> int:
    global _fail
    print("Demo anchor checks ->", BASE, "\n=== scripted queries (docs/DEMO.md + README table) ===")
    anchor("What was I reading about Microsoft Recall?", "Recall")
    anchor("Was I in any meetings?", "Zoom")
    anchor("What Supermemory docs did I look at?", "supermemory")
    anchor("What did I read about vector search and embeddings?", "HNSW")
    anchor("What did I copy to my clipboard?", "")   # any clipboard evidence

    print("\n=== time-scope correctness ===")
    j, _ = post("/api/ask", {"question": "What did I work on?", "scope": "today"})
    today = datetime.now().astimezone().date()
    dates = []
    for e in j.get("evidence", []):
        try:
            dates.append(datetime.fromisoformat(e["captured_at"]).astimezone().date())
        except Exception:  # noqa: BLE001
            pass
    all_today = dates and all(d == today for d in dates)
    print(f"  [{'PASS' if all_today else 'FAIL'}] scope=today -> {len(dates)} evidence, all dated today ({today}): {all_today}")
    if not all_today:
        _fail += 1

    print("\n=== digest ===")
    j, ms = post("/api/digest", {})
    ok = bool(j.get("answer")) and j.get("date")
    print(f"  [{'PASS' if ok else 'FAIL'}] digest today -> engine={j.get('engine')}, date={j.get('date')}, {len(j.get('evidence',[]))} ev, {ms:.0f}ms")
    if not ok:
        _fail += 1
    j2, _ = post("/api/digest", {"date": "2026-07-04"})
    okp = "answer" in j2
    print(f"  [{'PASS' if okp else 'FAIL'}] digest past date (2026-07-04) -> {len(j2.get('evidence',[]))} ev")
    if not okp:
        _fail += 1

    print(f"\n{'='*48}\nDEMO CHECK: {'ALL PASS' if _fail==0 else str(_fail)+' FAILED'}")
    return 0 if _fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
