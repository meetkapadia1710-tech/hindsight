# Hindsight — Pre-Submission Verification Report

Run: **2026-07-11**, against the real running stack (Supermemory Local :6767,
Ollama qwen2.5:3b-instruct :11434, app :8787, 540-memory demo container).

Legend: ✅ pass · ❌ fail · ⚠️ fixed (commit) · 🖐 needs manual (you)

Rerun the automated core anytime:
```powershell
py scripts\api_test.py     # 38 API-contract + XSS-logic + concurrency checks
py scripts\demo_check.py   # scripted demo anchors + time-scope + digest
py scripts\smoke_test.py   # add -> search -> forget round-trip (self-cleaning)
```

---

## Summary

- **Automated:** API 38/38, demo anchors ALL PASS, daemon capture+privacy live, fresh-venv install clean, XSS mitigated in-browser.
- **Fixes shipped:** SETUP.md model names (⚠️ `7f8c400`), credit-card clipboard filter (⚠️ `4aac2e6`).
- **No blockers found.** 3 items are 🖐 manual (Wi-Fi airplane loop, timed on-camera demo, 30-min soak).

---

## Phase 0 — Clean-clone / secrets / docs

| Check | Status | Evidence |
|---|---|---|
| Secret scan — full git history | ✅ | `git log -p --all \| grep` token patterns → only the literal regex strings in `config.toml`; no real `ghp_`/`sm_`/`github_pat_` values ever committed |
| Secret scan — working tree | ✅ | same; `.env` and `.hindsight/state.json` confirmed **not tracked** (`git check-ignore`) |
| `requirements.txt` fresh-venv install | ✅ | new venv, `pip install -r`, then `import httpx,psutil,fastapi,uvicorn,win32clipboard` → OK |
| Optional OCR deps marked optional | ✅ | winrt/Pillow are a commented block; base install needs none |
| Python version documented | ✅ | SETUP.md: "Python 3.11+ on Windows" |
| `config.toml` first-run defaults | ✅ | `ocr = false`, `host = 127.0.0.1`, `port = 8787` |
| No machine-specific paths in code/config | ✅ | grep for `C:\Users` / `/root/` / `meetk` in `hindsight/` + config → none |
| SETUP.md model names accurate | ⚠️ fixed | diagram/install/env said `llama3.2:3b`; changed to `qwen2.5:3b-instruct` (the model actually used) |
| README feature list matches reality | ✅ | Features + Changelog list live-feed, time-scope, digest, privacy center — all present |
| Full fresh-clone SETUP walkthrough (WSL + Ollama + Supermemory install) | 🖐 partial | The **start** path was validated cold this session (see Phase 6); a from-scratch WSL/Ollama/Supermemory reinstall was not re-run — the original install followed SETUP.md verbatim and the commands are current |

## Phase 1 — Backend API contract  → `scripts/api_test.py`: **38 passed, 0 failed**

| Check | Status | Evidence |
|---|---|---|
| `GET /api/health` up→ok:true | ✅ | `200 {ok:true}` |
| `GET /api/stats` count + speed | ✅ | `memoryCount=540`, warm **52ms** (<300ms), cold first-hit 76ms |
| `POST /api/ask` happy path + 7 evidence fields | ✅ | `{answer,engine,evidence}`, all of `content,memory,source,kind,captured_at,score,url` present |
| `/api/ask` abuse (empty, 5000-char, unicode, HTML, missing/0/9999/-5 limit, bad scope, wrong-type) | ✅ | no 5xx / no hang; wrong-type→422, rest 200 |
| `/api/recent` happy + bad limits | ✅ | `memories[]`; `limit=abc`→422, others 200 |
| `/api/digest` today + garbage/future/empty date | ✅ | 200 with `{answer,evidence,date}`; malformed dates → 200 (fallback to today) |
| `/api/forget_one` nonexistent / empty / missing id | ✅ | 502 / 400 / 422 — **never 500** |
| `/api/settings` GET + round-trip + malformed | ✅ | full state; junk body → 200/422, never 500; state restored after |
| `esc()` XSS logic escapes `& < > " '` and is used in attr contexts | ✅ | regex `/[&<>"']/g`; `href="${esc(…)}"`, `data-x="${esc(…)}"`, `k-${esc(k)}` |
| Concurrency: 5 simultaneous `/api/ask` | ✅ | all 5 → 200 with valid shape, ~10s total; stats coherent after |
| LLM-down → extractive fallback | ✅ | stop Ollama → `engine: extractive`, 6 evidence, instant |
| LLM recovers without app restart | ✅ | start Ollama → next ask `engine: ollama:qwen2.5:3b-instruct` |

## Phase 2 — Capture daemon

| Check | Status | Evidence |
|---|---|---|
| Clipboard capture → ingest (live) | ✅ | `daemon._tick()` into throwaway container: normal marker captured, searchable (`sent=1`) |
| Privacy filter drops secrets at ingestion (live) | ✅ | card number `4111 1111 1111 1111` **dropped** end-to-end (search finds normal, not card); throwaway container wiped after |
| Privacy filter unit matrix | ✅ | sk-/ghp_/AWS/private-key/card → DROPPED; normal text, phone, 10-digit id, date, ticket# → CAPTURED (no false positives) |
| Credit-card content not previously filtered | ⚠️ fixed | added `(?:\d[ -]?){13,16}` to `clipboard_deny_patterns` |
| Pause / per-source / exclusions honored | ✅ | daemon reads shared `.hindsight/state.json` each tick (`get_state()` gate in `_tick`); `/api/settings` round-trip verified in Phase 1; `is_excluded()` unit-verified |
| Window / browser-history / OCR capture | ✅ (prior) | verified with live evidence in the build sessions (window title + URL + OCR text ingested); OCR writes **no screenshot to disk** (text only) |
| Daemon survives Supermemory down | ✅ (code) | `Ingestor._send` catches per-event errors and keeps running; `client.ping()` gate on start |

## Phase 3 — Memory & answer quality  → `scripts/demo_check.py`: **ALL PASS**

| Check | Status | Evidence |
|---|---|---|
| All scripted demo anchors return expected evidence | ✅ | Recall→Ars Technica, "meetings"→Zoom, "supermemory docs"→overview, "vector search"→HNSW, "clipboard"→clip entry |
| Warm search latency ~100ms class | ✅ | stats 52ms; ask dominated by LLM, not search |
| **First-ask-after-restart latency (for camera)** | ✅ noted | ~**11s** on the first `/api/ask` (cold model load); ~3–5s after. **Warm the model off-camera** (DEMO.md already says so) |
| Time-scoped "today" correctness | ✅ | `scope=today` → 3 evidence, **all dated 2026-07-11** |
| Digest today + past date; extractive fallback | ✅ | today (8 ev) + `2026-07-04` (8 ev); extractive path proven in Phase 1 LLM-down |
| Relevance rules (≤0.15 of top, max 5, %=round(score·100)) | ✅ | enforced in `renderEvidence()`; evidence counts ≤5 across tests |

## Phase 4 — UI functional (desktop)

| Check | Status | Evidence |
|---|---|---|
| Core loop: query → answer → evidence → relevance bars → engine label | ✅ | ran live; evidence rendered with bars + `engine=ollama…` |
| Forget-all dialog: opens, focus→Cancel, Escape cancels | ✅ | in-page: dialog "Forget everything?", `activeElement=cancel`, Escape closes, count unchanged |
| **XSS render — thread evidence** | ✅ | payload memory renders as literal text (`&lt;img`), `img[onerror]`=0, alerts=0 |
| **XSS render — live feed** | ✅ | same payload in live drawer: escaped text, 0 imgs, 0 alerts |
| **XSS render — booby-trapped source URL** | ✅ | `href` kept whole value; `"` escaped so no `onmouseover` attribute breakout |
| Console clean during full session | ✅ | `read_console_messages onlyErrors` → none |
| Status badge flips on Supermemory stop/recover (~8s) | ✅ (prior) | verified with screenshots in build sessions (red "not reachable" ↔ green) |
| Live feed no-dup / no unbounded growth | ✅ (prior) | render keyed by id signature; only re-renders on change |

## Phase 5 — Responsive & a11y

| Check | Status | Evidence |
|---|---|---|
| 360px: no horizontal scroll, overflow menu, icon-only send, composer visible | ✅ | `scrollWidth==innerWidth==360`; measured this session |
| 412 / 600 / 905 / 1280 / 1536: no horizontal scroll | ✅ (prior) | measured in the responsive-pass commit; UI CSS unchanged since (only `esc()` touched) |
| Touch: hover-revealed actions reachable, ≥44px hit areas | ✅ | delete icon persistent on `hover:none`; 44px min via `pointer:coarse` block |
| Keyboard: tab order, focus rings, dialog focus-trap | ✅ (prior) | tabindex 1–9; dialog Tab/Shift+Tab trap verified |
| `prefers-reduced-motion` disables animation, app works | ✅ (prior) | media query covers ripple/spinner/live-item |
| Real phone on LAN, keyboard-open composer | 🖐 | open `http://<machine-ip>:8787` on a phone; `dvh` + `env(safe-area-inset-bottom)` in place |

## Phase 6 — Demo conditions

| Check | Status | Evidence |
|---|---|---|
| **Cold-start in documented order** | ✅ | from fully-down (WSL recycled), `scripts\start_supermemory.ps1` → server ready, key written, 540 intact, `HTTP 200` |
| Wrong-order / service-down recovery | ✅ | LLM-down handled (Phase 1); health badge reflects Supermemory down and recovers |
| **Wi-Fi-off full loop** | 🖐 + ✅ static | **static proof:** no external hosts referenced anywhere in `hindsight/` runtime code — all traffic is localhost:6767/:11434. Please still run it airplane-moded once on camera-day |
| **Timed 3-minute DEMO.md run** | 🖐 | run `docs/DEMO.md` top-to-bottom on record; warm the model off-camera first |
| **30-min long-run soak** | 🖐 | leave app + daemon running 30 min; watch for crashes / runaway CPU-RAM / stale live feed |

## Phase 7 — Repo state

| Check | Status | Evidence |
|---|---|---|
| One-command core checks documented | ✅ | `scripts/api_test.py`, `demo_check.py`, `smoke_test.py`; commands at top of this report |
| Fixes committed individually | ✅ | see commit hashes above |
| Report committed | ✅ | this file |

---

## 🖐 Manual checks awaiting you (camera-day, ~15 min total)

1. **Wi-Fi airplane-mode loop** — toggle airplane mode, then run ask / digest / live-capture / forget-one. (Everything is localhost, so it should just work — but prove it on camera.)
2. **Timed DEMO.md run** — record it top-to-bottom; **warm the model off-camera** (one throwaway question) so the first on-camera answer is ~2s not ~11s.
3. **30-minute soak** — app + `py -m hindsight.capture` running for 30 min; confirm no crash, no memory/CPU creep, live feed still updating.
4. *(optional)* **Real phone on LAN** — `http://<your-ip>:8787`, check the composer with the on-screen keyboard open.
