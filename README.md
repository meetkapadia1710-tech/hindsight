# Hindsight 🧠

**A photographic memory for your PC — that never leaves your PC.**

Hindsight quietly watches what you do on your machine (window titles, clipboard, browser history — screenshots+OCR optional), stores everything in [Supermemory Local](https://supermemory.ai/docs/self-hosting/overview), and lets you ask questions about your own past in plain English:

> *"What was that article about embeddings I read on Tuesday?"*
> *"What was I working on before lunch?"*
> *"Where did I copy that API key from?"* 😬

Think Microsoft Recall — except **nothing ever leaves your machine**. No cloud, no telemetry, no trust required. Turn off your Wi-Fi and it keeps working. That's the whole point.

Built for the **Supermemory localhost:6767 hackathon** (July 9–13, 2026).

---

## Why this exists

Microsoft Recall caused a privacy firestorm because a searchable log of everything you do is *incredibly useful* and *terrifying to put in anyone else's hands*. The answer isn't "don't build it" — it's **build it so it physically can't phone home**.

Supermemory Local makes that possible: embeddings, storage, and hybrid semantic search all run in one binary on localhost. Hindsight is the memory layer your PC always should have had.

## Architecture

```
┌─────────────────────────────── your machine ───────────────────────────────┐
│                                                                             │
│  ┌──────────────┐   events    ┌──────────────────┐   /v3/documents          │
│  │ capture      │ ──────────► │ batcher / dedupe │ ───────────────┐         │
│  │ daemon       │             │ + privacy filter │                ▼         │
│  │  · windows   │             └──────────────────┘   ┌────────────────────┐ │
│  │  · clipboard │                                    │ Supermemory Local  │ │
│  │  · browser   │                                    │  localhost:6767    │ │
│  │  · ocr (opt) │                                    │  embeddings+search │ │
│  └──────────────┘                                    └────────┬───────────┘ │
│                                                               │ /v3/search  │
│  ┌──────────────┐    ask      ┌──────────────────┐            │             │
│  │ web UI       │ ──────────► │ answer engine    │ ◄──────────┘             │
│  │ (chat +      │ ◄────────── │ (Ollama local ·  │                          │
│  │  timeline)   │   answer    │  extractive f/b) │                          │
│  └──────────────┘             └──────────────────┘                          │
│                                                                             │
└──────────────────────────── nothing leaves ─────────────────────────────────┘
```

## Privacy, by construction

- **All storage & search:** Supermemory Local on `localhost:6767`. Works offline.
- **Exclusion list:** password managers, private/incognito windows, and anything you add to `config.toml` are never captured.
- **Pause:** one keystroke suspends all capture.
- **Audit & delete:** the UI shows exactly what's stored; delete anything, or everything.

## Quickstart

```bash
# 1. Start Supermemory Local (one binary)
npx supermemory local        # → http://localhost:6767

# 2. Install & run Hindsight
pip install -r requirements.txt
python -m hindsight.capture   # start remembering
python -m hindsight.app       # ask questions → http://localhost:8787
```

## How it uses Supermemory Local

Every captured event (window focus, clipboard snippet, page visit, OCR text) becomes a document via `POST /v3/documents` with rich metadata (timestamp, source app, url). Questions hit `POST /v3/search` (hybrid semantic search) and the top memories are synthesized into an answer by a local model — with an evidence timeline so you can verify every claim. Supermemory Local isn't a feature of Hindsight; it's the reason Hindsight can exist.

## Team

- Meet Kapadia — solo

## License

MIT
