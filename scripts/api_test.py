"""Backend API contract + robustness tests for the Hindsight app.

    python scripts/api_test.py            # run the full suite
    python scripts/api_test.py --quick    # skip the concurrency stress test

Hits the real running app at http://localhost:8787 (start it with
`py -m hindsight.app`). Tests happy paths, malformed inputs, no-500 guarantees,
evidence-field completeness, concurrency, and the client-side XSS-escape logic.
Non-destructive: never calls /api/forget_all; forget_one only with a fake id.

Exits non-zero if any check fails, so it doubles as a pre-demo gate.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:  # keep output readable if a terminal is on a legacy code page
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# 127.0.0.1, not "localhost": Python's urllib on Windows tries IPv6 (::1) first
# and eats a ~2s timeout before falling back, which would skew latency numbers.
# Browsers use happy-eyeballs and don't hit this, so real client latency matches
# the 127.0.0.1 path measured here.
BASE = "http://127.0.0.1:8787"
ROOT = Path(__file__).resolve().parent.parent

_passed = 0
_failed = 0


def _check(name: str, ok: bool, detail: str = "") -> bool:
    global _passed, _failed
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    if ok:
        _passed += 1
    else:
        _failed += 1
    return ok


def call(method: str, path: str, body=None, timeout: float = 30.0):
    """Return (status, json_or_text, elapsed_ms). Never raises on HTTP error."""
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except Exception as e:  # noqa: BLE001
        return 0, str(e), (time.time() - t) * 1000
    ms = (time.time() - t) * 1000
    try:
        return status, json.loads(raw), ms
    except ValueError:
        return status, raw, ms


def section(title: str):
    print(f"\n=== {title} ===")


# --------------------------------------------------------------------------
def test_health():
    section("GET /api/health")
    s, j, _ = call("GET", "/api/health")
    _check("200 + ok:true (Supermemory up)", s == 200 and isinstance(j, dict) and j.get("ok") is True, f"status={s} body={j}")


def test_stats():
    section("GET /api/stats")
    cold = call("GET", "/api/stats")[2]
    time.sleep(2)   # the first calls after an app restart warm the SM connection pool
    times = [call("GET", "/api/stats")[2] for _ in range(6)]
    s, j, _ = call("GET", "/api/stats")
    warm = min(times)
    _check("200 + integer memoryCount", s == 200 and isinstance(j.get("memoryCount"), int), f"body={j}")
    _check("responds < 300ms warm", warm < 300, f"warm={warm:.0f}ms (cold first-hit {cold:.0f}ms)")


def test_ask():
    section("POST /api/ask — happy path + evidence fields")
    s, j, ms = call("POST", "/api/ask", {"question": "what did I read about vector search?"})
    ok = s == 200 and all(k in j for k in ("answer", "engine", "evidence"))
    _check("200 + {answer, engine, evidence}", ok, f"engine={j.get('engine')} ev={len(j.get('evidence', []))} {ms:.0f}ms")
    if ok and j["evidence"]:
        fields = {"content", "memory", "source", "kind", "captured_at", "score", "url"}
        first = j["evidence"][0]
        _check("evidence items carry all fields", fields <= set(first), f"missing={fields - set(first)}")

    section("POST /api/ask — malformed inputs must not 500 / hang")
    cases = {
        "empty question": {"question": ""},
        "5000-char question": {"question": "x " * 2500},
        "unicode + emoji": {"question": "café ☕ 日本語 recall?"},
        "HTML/script in question": {"question": "<img src=x onerror=alert(1)><script>alert(2)</script>"},
        "missing limit (default)": {"question": "hello"},
        "limit: 0": {"question": "hello", "limit": 0},
        "limit: 9999": {"question": "hello", "limit": 9999},
        "limit: -5": {"question": "hello", "limit": -5},
        "bad scope value": {"question": "hello", "scope": "not-a-scope"},
        "wrong type question": {"question": 12345},
    }
    for name, body in cases.items():
        s, j, ms = call("POST", "/api/ask", body, timeout=40)
        _check(f"no 500/hang: {name}", s in (200, 400, 422) and ms < 40000, f"status={s} {ms:.0f}ms")


def test_recent():
    section("POST/GET /api/recent")
    s, j, _ = call("GET", "/api/recent?limit=5")
    _check("200 + memories[]", s == 200 and isinstance(j.get("memories"), list), f"n={len(j.get('memories', []))}")
    for q in ["?limit=0", "?limit=9999", "?limit=-1", "?limit=abc"]:
        s, j, _ = call("GET", "/api/recent" + q)
        _check(f"no 500: limit{q}", s in (200, 400, 422), f"status={s}")


def test_digest():
    section("POST /api/digest")
    s, j, ms = call("POST", "/api/digest", {}, timeout=40)
    _check("200 + {answer, evidence, date}", s == 200 and "answer" in j and "evidence" in j, f"engine={j.get('engine')} {ms:.0f}ms")
    for name, body in {"garbage date": {"date": "not-a-date"}, "future date": {"date": "2099-01-01"}, "empty": {"date": ""}}.items():
        s, j, _ = call("POST", "/api/digest", body, timeout=40)
        _check(f"no 500: {name}", s == 200, f"status={s}")


def test_forget_one():
    section("POST /api/forget_one — bad input must not 500")
    for name, body in {"nonexistent id": {"id": "doesnotexist123"}, "empty id": {"id": ""}, "missing id": {}}.items():
        s, j, _ = call("POST", "/api/forget_one", body)
        _check(f"graceful: {name}", s in (200, 400, 422, 502) and s != 500, f"status={s}")


def test_settings():
    section("GET/POST /api/settings")
    s, orig, _ = call("GET", "/api/settings")
    ok = s == 200 and all(k in orig for k in ("paused", "sources", "exclusions"))
    _check("GET returns full state", ok, f"body={orig}")
    s, j, _ = call("POST", "/api/settings", {"exclusions": []})
    _check("POST no-op accepted", s == 200, f"status={s}")
    for name, body in {"bad type": {"paused": "yes"}, "junk key": {"nope": 1}, "sources junk": {"sources": "x"}}.items():
        s, j, _ = call("POST", "/api/settings", body)
        _check(f"no 500: {name}", s in (200, 400, 422), f"status={s}")
    # restore original state so the suite has no side effect on the daemon
    if isinstance(orig, dict):
        call("POST", "/api/settings", {"paused": orig.get("paused", False),
                                       "sources": orig.get("sources", {}),
                                       "exclusions": orig.get("exclusions", [])})


def test_concurrency():
    section("Concurrency — 5 simultaneous /api/ask")
    qs = [f"query number {i} about embeddings" for i in range(5)]
    t = time.time()
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(lambda q: call("POST", "/api/ask", {"question": q}, timeout=60), qs))
    ms = (time.time() - t) * 1000
    all_ok = all(s == 200 and isinstance(j.get("evidence"), list) for s, j, _ in results)
    _check("all 5 completed with valid shape", all_ok, f"{ms:.0f}ms total")


def test_xss_escape_logic():
    section("XSS — client escape() logic (extracted from ui.py)")
    ui = (ROOT / "hindsight" / "app" / "ui.py").read_text(encoding="utf-8")
    m = re.search(r"function esc\(s\)\{[^\n]*\}", ui)
    if not _check("esc() found in ui.py", bool(m)):
        return
    esc_src = m.group(0)
    ok_chars = all(c in esc_src for c in ["&amp;", "&lt;", "&gt;", "&quot;", "&#39;"])
    _check("esc escapes & < > \" '", ok_chars, esc_src[:80])
    # confirm attribute-context interpolations pass through esc()
    for pat in [r'href="\$\{esc\(', r'data-x="\$\{esc\(', r'k-\$\{esc\(k\)']:
        _check(f"attr uses esc: {pat}", re.search(pat, ui) is not None)


def main() -> int:
    quick = "--quick" in sys.argv
    print("Hindsight API contract tests ->", BASE)
    # fail fast if the app isn't up
    s, _, _ = call("GET", "/api/health", timeout=5)
    if s == 0:
        print("\nAPP NOT REACHABLE at", BASE, "— start it with `py -m hindsight.app`")
        return 2
    test_health()
    test_stats()
    test_ask()
    test_recent()
    test_digest()
    test_forget_one()
    test_settings()
    test_xss_escape_logic()
    if not quick:
        test_concurrency()
    print(f"\n{'='*48}\nAPI TESTS: {_passed} passed, {_failed} failed")
    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
