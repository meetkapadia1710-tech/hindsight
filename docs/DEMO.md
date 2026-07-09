# Hindsight — 3-minute demo script

Target: ≤ 3:00. Record at 1080p. Keep the terminal + browser side by side.

## Before you hit record
- `scripts\start_supermemory.ps1` — server up, `.env` has the key.
- `py scripts\seed_demo.py` — a believable day of activity is in memory.
- `py -m hindsight.app` — open http://localhost:8787 (shows "13 memories remembered").
- Have a terminal ready running (or ready to run) `py -m hindsight.capture`.

## Beat sheet

**0:00–0:20 — The hook.**
> "This is Hindsight. It gives your PC a photographic memory — every window,
> everything you copy, every page you read — and lets you ask about your own
> past in plain English. The twist: none of it ever leaves your machine."

Show the app. Point at the header: **"13 memories remembered · Local · Offline-capable."**

**0:20–1:05 — Ask your past.**
Type, one at a time (let each answer + evidence render):
- *"What was I reading about Microsoft Recall?"* → grounded answer + the Ars Technica card.
- *"Was I in any meetings today?"* → the Zoom hackathon office hours.
- *"What did I copy to my clipboard?"* → the clipboard entries.
> "Every answer is written by a local model and backed by an evidence
> timeline — real memories with timestamps and sources. Nothing is made up."

**1:05–1:45 — It's actually live.**
Switch to the terminal, run `py -m hindsight.capture`. Open a browser tab to an
article, copy a line of text. Back in the app, ask about what you just did.
> "The capture daemon is watching window titles, the clipboard, and browser
> history — with a privacy filter that drops password managers and anything
> that looks like a secret."

**1:45–2:25 — The money shot: pull the plug.**
Turn off Wi‑Fi (toggle it on camera). Ask another question. It still answers.
> "Embeddings, storage, search, and the language model all run on localhost
> through Supermemory Local. Turn off the internet and your second brain keeps
> working. This is the whole point — a Recall you can actually trust."

**2:25–2:55 — Your data, your call.**
Click **Forget all**, confirm. Header drops to "0 memories."
> "And because it's yours, you can wipe every memory in one click. Local by
> construction, private by design."

**2:55–3:00 — Close.**
> "Hindsight. Your PC's memory — that never leaves your PC. Built on
> Supermemory Local."

## Tips
- Pre-load the model once before recording (first Ollama call warms it) so
  answers come back in ~1–2s on camera.
- If an answer is slow, the extractive fallback still shows the right memories
  instantly — the evidence timeline is the star either way.
