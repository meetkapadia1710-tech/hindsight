# Hindsight — 3-minute demo script

Target: ≤ 3:00. Record at 1080p. Keep a browser tab + the Hindsight app side by side.

## Before you hit record
- `scripts\start_supermemory.ps1` — server up, `.env` has the key.
- `py scripts\seed_bulk.py 540` — a believable *month* of activity is in memory.
- `py -m hindsight.app` — open http://localhost:8787 (header shows "540 memories remembered").
- Warm the model once (ask any question and discard) so answers come back in ~1–2s.
- Optional: have a terminal ready to run `py -m hindsight.capture` for the live loop.

## Beat sheet

**0:00–0:15 — The hook.**
> "This is Hindsight — a photographic memory for your PC that never leaves your
> PC. 540 memories of what I've read, copied, and done, all searchable, all
> local."

Point at the header: **"540 memories remembered · Local · Offline-capable."**

**0:15–1:00 — The live loop (the money shot).** *Open the **Live** drawer.*
Copy a line of text on camera (e.g. a sentence from an article).
> "Watch the feed — I just copied that, and Hindsight remembered it in real
> time."

The new memory slides in at the top of the Live drawer. Immediately ask about it:
> "…and I can already ask about it."

Type a question referencing what you just copied → grounded answer with that
memory as evidence. **That closed loop — copy → remembered → answered — is the
whole product in 30 seconds.**

**1:00–1:35 — Ask your past, scoped in time.**
Ask *"What was I reading about Microsoft Recall?"* → grounded answer + the Ars
Technica card with a relevance bar. Then tap the **Today** chip and ask
*"What did I work on?"* → answer card tagged **Scope · Today**, evidence all
from today.
> "Every answer is written by a local model, backed by an evidence timeline —
> real memories with timestamps and sources — and I can scope recall to today,
> yesterday, or this week."

**1:35–2:05 — Summarize my day.**
Click **Summarize my day**.
> "One click, and it narrates my whole day from 540 memories — morning research,
> afternoon coding, the sites and apps — every line backed by evidence."

**2:05–2:40 — Your memory, your rules (vs. Recall).** *Open **Privacy**.*
> "Microsoft Recall got recalled because users had no control. Here: pause
> capture…" *(toggle — the app bar flips to a red PAUSED)* "…turn any source
> off, exclude a domain like my bank…" *(add `chase.com`)* "…delete a single
> memory…" *(trash-icon a row)* "…or burn it all." *(Forget all → confirm →
> header hits 0, then don't save — or re-seed after)*
> "Pause, per-source, per-memory, per-domain, or everything. Your memory, your
> rules."

**2:40–2:55 — Pull the plug.**
Turn off Wi‑Fi on camera. Ask another question. It still answers.
> "Embeddings, storage, search, and the language model all run on localhost
> through Supermemory Local. Wi-Fi off — my second brain keeps working."

**2:55–3:00 — Close.**
> "Hindsight. Your PC's memory — that never leaves your PC. Built on
> Supermemory Local."

## Tips
- If the GPU is busy and an answer is slow, the instant extractive fallback
  still shows the right evidence — the timeline is the star either way.
- If you demo **Forget all** on camera, re-seed afterward with
  `py scripts\seed_bulk.py 540` before the next take.
- Free VRAM before recording (close other GPU apps) so answers stay ~1–2s;
  `ollama stop qwen2.5:3b-instruct` frees ~2 GB when you're done.
