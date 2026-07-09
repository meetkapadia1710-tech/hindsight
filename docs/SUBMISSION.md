# Submission content (localhost:6767 hackathon)

Deadline: **Sunday, July 13, 2026 · 23:59 PST**. Both steps required:
1. Google Form → https://forms.gle/ARXHNpFY5VNfiNDBA
2. Discord #showcase post (pinned template)

---

## #showcase post (pinned template)

**Project name:** Hindsight

**One-line pitch:** A photographic memory for your PC that never leaves your PC — ask your own past in plain English, 100% local.

**Team:** Meet Kapadia (solo)

**Repo:** <REPO_URL>

**Demo video:** <VIDEO_URL>

**How it uses Supermemory Local (3–5 sentences):**
Hindsight captures your computer activity — active window titles, clipboard, and browser history — and stores each event as a memory in Supermemory Local via `POST /v4/memories`. Supermemory embeds every memory on-device with its bundled model and keeps them in its encrypted local store, so all recall happens over `localhost:6767` with nothing sent to the cloud. When you ask a question, Hindsight uses Supermemory Local's `/v4/search` for semantic recall and a local Ollama model synthesizes a cited answer with an evidence timeline. Supermemory Local is the reason the product can exist: it's what makes a private, offline "Microsoft Recall" possible — turn off the Wi-Fi and it still works. A one-click "Forget all" wipes everything, because the data is yours.

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
- **Repo:** <REPO_URL>
- **Demo video:** <VIDEO_URL>

---

## Elevator framing (if asked to describe in one breath)
"Microsoft Recall caused a privacy firestorm because nobody wants a searchable
log of their screen in someone else's cloud. Hindsight is that product built so
it physically can't phone home — Supermemory Local runs the entire memory layer
on your laptop, so your second brain is finally yours."
