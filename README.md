# Hindsight 🧠

**A photographic memory for your PC — that never leaves your PC.**

Hindsight quietly watches what you do on your machine (window titles, clipboard, browser history — screenshots+OCR optional), stores everything in [Supermemory Local](https://supermemory.ai/docs/self-hosting/overview), and lets you ask questions about your own past in plain English:

> *"What was that article about embeddings I read on Tuesday?"*
> *"What was I working on before lunch?"*
> *"Where did I copy that API key from?"* 😬

Think Microsoft Recall — except **nothing ever leaves your machine**. No cloud, no telemetry, no trust required. Turn off your Wi-Fi and it keeps working. That's the whole point.

Built for the **Supermemory localhost:6767 hackathon** (July 9–13, 2026).

---

## See it in action

![Hindsight answering a question, with a local answer and an evidence timeline](docs/demo.svg)

Ask in plain English; get a cited answer plus an **evidence timeline** — the real
memories behind it, each with a timestamp, source, and relevance score:

| You ask | Hindsight answers (from your own activity) |
| --- | --- |
| *"What was I reading about Microsoft Recall?"* | "How Microsoft Recall stores screenshots" — Ars Technica |
| *"Was I in any meetings?"* | Zoom Meeting — Supermemory hackathon office hours |
| *"What Supermemory docs did I look at?"* | Supermemory self-hosting overview |
| *"What did I read about vector search & embeddings?"* | the HNSW article, the bge model card, a copied cosine-similarity formula |
| *"What did I copy to my clipboard?"* | `npx supermemory local`, the submission form link, … |

> 📹 **Demo video:** _add your recording here_ — see [`docs/DEMO.md`](docs/DEMO.md)
> for the 3‑minute script (including the "turn the Wi‑Fi off, it still answers" moment).
> To drop in a real screen capture, save it as `docs/demo.gif` and swap the image link above.

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

Supermemory Local's binary is Linux/macOS-only, so on Windows it runs inside
WSL2 while Hindsight runs natively. Full steps are in [SETUP.md](SETUP.md);
the short version:

```powershell
# 1. One-time: install the Linux side (Supermemory Local + Ollama) in WSL2
#    → see SETUP.md

# 2. Start the server (boots Supermemory + Ollama in WSL, writes the API key)
scripts\start_supermemory.ps1        # → http://localhost:6767

# 3. Install & run Hindsight (native Windows)
pip install -r requirements.txt
py -m hindsight.capture              # start remembering  (Ctrl+Break pauses)
py -m hindsight.app                  # ask questions → http://localhost:8787
```

## How it uses Supermemory Local

Every captured event (window focus, clipboard snippet, page visit, optional
OCR text) is phrased as a factual sentence and stored as a memory via
Supermemory Local's `POST /v4/memories` — embedded **on-device** (the bundled
`bge` model) into Supermemory's encrypted local store. Questions hit
`POST /v4/search` for hybrid semantic recall, and the top memories are
synthesized into a cited answer by a local model (Ollama), with an evidence
timeline so you can verify every claim. Storage, embeddings, and search all
run on `localhost:6767` — nothing leaves the machine, so it keeps working
with the Wi‑Fi off. Supermemory Local isn't a feature of Hindsight; it's the
reason Hindsight can exist.

## Team

- Meet Kapadia — solo

## License

MIT
