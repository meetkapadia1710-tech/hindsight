# Setting up Hindsight on Windows

Hindsight runs the **Supermemory Local** memory server inside **WSL2 (Ubuntu)**
— Supermemory's binary is Linux/macOS only — while the **capture daemon** and
**query app** run natively on Windows (that's where your windows, clipboard,
and browser history actually are). WSL2 forwards `localhost:6767` to Windows
automatically, so the two halves talk over `localhost` with zero config.

```
Windows (native Python)                     WSL2 · Ubuntu
┌───────────────────────┐                   ┌────────────────────────────┐
│ capture daemon        │  localhost:6767   │ supermemory-server         │
│ query app :8787       │ ────────────────► │  · local embeddings (bge)  │
└───────────────────────┘                   │  · encrypted local storage │
                                            │  · memory agent → Ollama   │
                                            │ ollama :11434 (llama3.2)   │
                                            └────────────────────────────┘
```

Everything above runs on your machine. Turn off Wi-Fi and it still answers.

## Prerequisites

- Windows 11 with WSL2 (`wsl --version` ≥ 2.0)
- Python 3.11+ on Windows

## 1. Install the Linux side (one time)

```powershell
wsl --install -d Ubuntu-24.04 --no-launch
wsl -d Ubuntu-24.04 -u root -- bash -lc "apt-get update && apt-get install -y zstd"
```

Install Supermemory Local:

```powershell
wsl -d Ubuntu-24.04 -u root -- bash -lc "curl -fsSL https://supermemory.ai/install | bash"
```

Install Ollama + the local model (powers Supermemory's memory agent, fully offline):

```powershell
wsl -d Ubuntu-24.04 -u root -- bash -lc "curl -fsSL https://ollama.com/install.sh | sh"
wsl -d Ubuntu-24.04 -u root -- bash -lc "ollama serve >/root/ollama.log 2>&1 & sleep 3; ollama pull llama3.2:3b"
```

Point Supermemory's memory agent at Ollama:

```bash
# /root/.supermemory/env
OPENAI_API_KEY='ollama'
OPENAI_BASE_URL='http://localhost:11434/v1'
OPENAI_MODEL='llama3.2:3b'
```

## 2. Start the server

```powershell
scripts\start_supermemory.ps1     # boots ollama + supermemory-server in WSL, waits for :6767
```

On first boot it downloads a ~106MB local embedding model (once). When ready it
prints an `sm_...` API key — it's saved to `.env` automatically by the script.

## 3. Run Hindsight (Windows)

```powershell
pip install -r requirements.txt
py -m hindsight.capture      # start remembering (Ctrl+C to stop, Ctrl+Break to pause)
py -m hindsight.app          # ask questions → http://localhost:8787
```

## Privacy controls

- `config.toml` → `[privacy]` — exclude apps/titles, drop secret-shaped clipboard text.
- Ctrl+Break in the capture window pauses all capture.
- The app's audit view lists what's stored and can wipe it.
