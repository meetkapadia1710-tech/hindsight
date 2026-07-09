<#
  Starts Ollama + Supermemory Local inside WSL2 (Ubuntu-24.04) and waits until
  the server is reachable from Windows at http://localhost:6767. Writes the
  auto-generated API key into .env. Idempotent: safe to run repeatedly.
#>
param(
  [string]$Distro = "Ubuntu-24.04",
  [int]$Port = 6767,
  [int]$TimeoutSec = 180
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"

Write-Host "[hindsight] ensuring Ollama + Supermemory are running in $Distro..." -ForegroundColor Cyan

# Launch a detached, windowless WSL session that keeps the server alive.
# Ollama runs as a systemd service (auto-started); we make sure it's up, then
# source the env file (Ollama endpoint, data dir, port) and exec the server in
# the foreground so the WSL instance stays alive with it. Note: the process
# name is truncated to 15 chars, so we match "supermemory-ser".
$launch = @'
pgrep -x supermemory-ser >/dev/null && exit 0
systemctl start ollama 2>/dev/null || (pgrep -x ollama >/dev/null || nohup ollama serve >/root/ollama.log 2>&1 &)
set -a; . /root/.supermemory/env; set +a
exec /root/.supermemory/bin/supermemory-server >/root/sm.log 2>&1
'@
Start-Process -WindowStyle Hidden -FilePath "wsl.exe" `
  -ArgumentList @("-d", $Distro, "-u", "root", "--", "bash", "-lc", $launch)

# Poll from Windows until the server answers on localhost.
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$ready = $false
while ((Get-Date) -lt $deadline) {
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:$Port/" -TimeoutSec 3 -UseBasicParsing
    if ($r.StatusCode -ge 200) { $ready = $true; break }
  } catch { Start-Sleep -Milliseconds 1500 }
}

if (-not $ready) {
  Write-Host "[hindsight] server did not become ready in $TimeoutSec s." -ForegroundColor Red
  Write-Host "  Check the log:  wsl -d $Distro -u root -- tail -30 /root/sm.log"
  exit 1
}

# Pull the auto-generated API key out of the server log and persist it.
$key = (wsl -d $Distro -u root -- bash -lc "grep -oE 'sm_[A-Za-z0-9_]+' /root/sm.log | head -1").Trim()
if ($key) {
  "SUPERMEMORY_API_KEY=$key" | Out-File -FilePath $envFile -Encoding ascii
  Write-Host "[hindsight] server ready. API key written to .env" -ForegroundColor Green
} else {
  Write-Host "[hindsight] server ready (localhost auto-auth; no key found in log)." -ForegroundColor Green
}
Write-Host "  URL: http://localhost:$Port"
