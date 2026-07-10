# Submission content (localhost:6767 hackathon)

Deadline: **Sunday, July 13, 2026 · 23:59 PST**. Both steps required:
1. Google Form → https://forms.gle/ARXHNpFY5VNfiNDBA
2. Discord #showcase post (pinned template)

---

## #showcase post (pinned template)

**Project name:** Hindsight

**One-line pitch:** A photographic memory for your PC that never leaves your PC — ask your own past in plain English, 100% local.

**Team:** Meet Kapadia (solo)

**Repo:** https://github.com/meetkapadia1710-tech/hindsight

**Demo video:** <VIDEO_URL>

**How it uses Supermemory Local (3–5 sentences):**
Hindsight streams your computer activity — window titles, clipboard, browser history, and opt-in screen OCR — into Supermemory Local as memories via `POST /v4/memories`, embedded on-device with its bundled model and held in its encrypted local store, so all recall happens over `localhost:6767` with nothing sent to the cloud. It leans on Supermemory well past store-and-search: a **live feed** tails the newest memories by insertion time so you literally watch memory form; **time-scoped questions** pull a wide `/v4/search` candidate set and filter by each memory's `captured_at` metadata to answer "what did I do today / yesterday / this week"; and a **daily digest** lists a whole day's memories and narrates them, grouped by site and app. Every answer is grounded in a `/v4/search` evidence timeline, and the same memory layer powers total user control — **per-memory delete** (`/v4/memories` DELETE), pause capture, per-source toggles, and per-domain exclusions. All of it runs against a **540-memory** local container and keeps working with the Wi‑Fi off. Supermemory Local isn't a feature of Hindsight — it's the reason a private, offline "Microsoft Recall" can exist at all.

---

## Google Form — draft answers

- **Project name:** Hindsight
- **What it does:** Passive, privacy-first "second brain" for Windows. It records
  what you do (windows, clipboard, browser history), stores it in Supermemory
  Local, and answers natural-language questions about your past with a cited
  evidence timeline — fully offline.
- **How it uses Supermemory Local:** (see the 5-sentence paragraph above)
- **Tech:** Python capture daemon + FastAPI app (native Windows); Supermemory
  Local + Ollama (qwen2.5:3b) running in WSL2; on-device bge embeddings; all on
  localhost:6767 / :11434 / :8787.
- **What's new / built during the window:** everything in the repo (see commit
  history July 9–13).
- **Repo:** https://github.com/meetkapadia1710-tech/hindsight
- **Demo video:** <VIDEO_URL>

---

## Elevator framing (if asked to describe in one breath)
"Microsoft Recall caused a privacy firestorm because nobody wants a searchable
log of their screen in someone else's cloud. Hindsight is that product built so
it physically can't phone home — Supermemory Local runs the entire memory layer
on your laptop, so your second brain is finally yours."
