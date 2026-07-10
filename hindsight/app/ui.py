"""The single-page UI, inlined so the app is one importable module with no
static-file plumbing. Vanilla JS, no build step, no external requests."""

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Hindsight</title>
<style>
  :root {
    --bg: #0b0d10; --panel: #14181d; --panel-2: #1b2027;
    --line: #262c34; --text: #e8ecf1; --muted: #8a94a3;
    --accent: #5b9dff; --accent-2: #7c5cff; --good: #37d39b;
    --clip: #ffb454; --win: #5b9dff; --browser: #37d39b; --ocr: #ff7ab6;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: radial-gradient(1200px 600px at 70% -10%, #1a2130 0%, var(--bg) 55%);
    color: var(--text); font: 15px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif;
    min-height: 100vh;
  }
  header {
    display: flex; align-items: center; gap: 14px; padding: 18px 28px;
    border-bottom: 1px solid var(--line); position: sticky; top: 0;
    background: rgba(11,13,16,.8); backdrop-filter: blur(10px); z-index: 5;
  }
  .logo { font-size: 22px; font-weight: 700; letter-spacing: -.02em; }
  .logo span { background: linear-gradient(90deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .tag { color: var(--muted); font-size: 13px; }
  .hstats { margin-left: auto; color: var(--muted); font-size: 12.5px; }
  .forget {
    background: transparent; border: 1px solid var(--line); color: var(--muted);
    border-radius: 999px; padding: 6px 12px; font-size: 12.5px; cursor: pointer;
    transition: .15s;
  }
  .forget:hover { border-color: #ff5c5c; color: #ff5c5c; }
  .badge {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px;
    font-size: 12.5px; color: var(--good); background: rgba(55,211,155,.06);
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--good);
    box-shadow: 0 0 10px var(--good); }
  .dot.off { background: #ff5c5c; box-shadow: 0 0 10px #ff5c5c; }
  main { max-width: 900px; margin: 0 auto; padding: 28px 20px 140px; }
  .hero { text-align: center; margin: 26px 0 30px; }
  .hero h1 { font-size: 30px; margin: 0 0 8px; letter-spacing: -.03em; }
  .hero p { color: var(--muted); margin: 0; }
  .chips { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
    margin-top: 20px; }
  .chip { padding: 8px 14px; border: 1px solid var(--line); border-radius: 10px;
    background: var(--panel); color: var(--text); cursor: pointer; font-size: 13.5px;
    transition: .15s; }
  .chip:hover { border-color: var(--accent); background: var(--panel-2); }
  .thread { display: flex; flex-direction: column; gap: 22px; margin-top: 10px; }
  .msg { display: flex; gap: 12px; }
  .msg .who { width: 30px; height: 30px; border-radius: 8px; flex: none;
    display: grid; place-items: center; font-size: 14px; }
  .msg.user .who { background: var(--panel-2); }
  .msg.ai .who { background: linear-gradient(135deg, var(--accent), var(--accent-2)); }
  .bubble { background: var(--panel); border: 1px solid var(--line);
    border-radius: 12px; padding: 14px 16px; flex: 1; white-space: pre-wrap; }
  .msg.user .bubble { background: var(--panel-2); }
  .engine { font-size: 11.5px; color: var(--muted); margin-top: 10px; }
  .evidence { margin-top: 14px; border-top: 1px dashed var(--line); padding-top: 12px; }
  .evidence h4 { margin: 0 0 10px; font-size: 12px; text-transform: uppercase;
    letter-spacing: .08em; color: var(--muted); }
  .ev { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--line); }
  .ev:last-child { border-bottom: 0; }
  .ev .rail { width: 3px; border-radius: 2px; flex: none; }
  .ev.kind-clipboard .rail { background: var(--clip); }
  .ev.kind-window .rail { background: var(--win); }
  .ev.kind-browser .rail { background: var(--browser); }
  .ev.kind-ocr .rail { background: var(--ocr); }
  .ev .body { flex: 1; min-width: 0; }
  .ev .content { font-size: 13.5px; }
  .ev .meta { font-size: 11.5px; color: var(--muted); margin-top: 3px; word-break: break-word; }
  .ev .relev { flex: none; align-self: center; display: flex; align-items: center; gap: 7px;
    font-size: 11px; color: var(--muted); }
  .ev .relev .bar { width: 44px; height: 5px; border-radius: 3px; background: var(--panel-2);
    overflow: hidden; }
  .ev .relev .bar > span { display: block; height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
  .composer { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(180deg, transparent, var(--bg) 30%); padding: 20px; }
  .composer .box { max-width: 900px; margin: 0 auto; display: flex; gap: 10px; }
  input[type=text] { flex: 1; background: var(--panel); border: 1px solid var(--line);
    border-radius: 12px; padding: 14px 16px; color: var(--text); font-size: 15px; outline: none; }
  input[type=text]:focus { border-color: var(--accent); }
  button.send { background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border: 0; color: white; font-weight: 600; padding: 0 22px; border-radius: 12px;
    cursor: pointer; font-size: 15px; }
  button.send:disabled { opacity: .5; cursor: default; }
  .spin { display: inline-block; width: 14px; height: 14px; border: 2px solid #fff5;
    border-top-color: #fff; border-radius: 50%; animation: s .7s linear infinite; }
  @keyframes s { to { transform: rotate(360deg); } }
  a { color: var(--accent); }
</style>
</head>
<body>
<header>
  <div class="logo">Hind<span>sight</span></div>
  <div class="tag">your PC's memory · stays on your PC</div>
  <div class="hstats" id="hstats"></div>
  <button class="forget" id="forget" title="Permanently delete every stored memory">Forget all</button>
  <div class="badge" id="badge"><span class="dot" id="dot"></span><span id="badgetext">checking…</span></div>
</header>
<main>
  <div class="hero" id="hero">
    <h1>Ask your past.</h1>
    <p>Everything you've seen, copied, and read — searchable, and 100% local.</p>
    <div class="chips" id="chips">
      <div class="chip">What was I working on this morning?</div>
      <div class="chip">What articles did I read about embeddings?</div>
      <div class="chip">What did I copy to my clipboard earlier?</div>
      <div class="chip">Which GitHub repos did I look at today?</div>
    </div>
  </div>
  <div class="thread" id="thread"></div>
</main>
<div class="composer">
  <div class="box">
    <input id="q" type="text" placeholder="Ask about anything you've done on this machine…" autocomplete="off" />
    <button class="send" id="send">Recall</button>
  </div>
</div>
<script>
const $ = s => document.querySelector(s);
const thread = $('#thread'), input = $('#q'), send = $('#send');

async function health() {
  try {
    const r = await fetch('/api/health'); const j = await r.json();
    $('#dot').classList.toggle('off', !j.ok);
    $('#badgetext').textContent = j.ok ? 'Local · Offline-capable' : 'Supermemory Local not reachable';
  } catch { $('#dot').classList.add('off'); $('#badgetext').textContent = 'offline'; }
}
health(); setInterval(health, 8000);

async function refreshStats(){
  try { const r = await fetch('/api/stats'); const j = await r.json();
    $('#hstats').textContent = (j.memoryCount || 0) + ' memories remembered';
  } catch {}
}
refreshStats(); setInterval(refreshStats, 8000);
$('#forget').onclick = async () => {
  if(!confirm('Permanently delete every stored memory? This cannot be undone.')) return;
  await fetch('/api/forget_all', {method:'POST'});
  thread.innerHTML=''; $('#hero').style.display='';
  refreshStats();
};

const KIND_ICON = { clipboard:'📋', window:'🪟', browser:'🌐', ocr:'👁️' };
function esc(s){ return (s||'').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

function addUser(text){
  const el = document.createElement('div'); el.className = 'msg user';
  el.innerHTML = `<div class="who">🧑</div><div class="bubble">${esc(text)}</div>`;
  thread.appendChild(el); scroll();
}
function addAI(){
  const el = document.createElement('div'); el.className = 'msg ai';
  el.innerHTML = `<div class="who">🧠</div><div class="bubble"><span class="spin"></span></div>`;
  thread.appendChild(el); scroll(); return el;
}
function renderEvidence(ev){
  if(!ev || !ev.length) return '';
  // Keep the clearly-relevant matches: within 0.15 of the best score, max 5.
  const top = ev[0].score || 0;
  const shown = ev.filter(e => (e.score||0) >= top - 0.15).slice(0,5);
  const rows = shown.map(e => {
    const k = e.kind || 'window';
    const when = e.captured_at ? new Date(e.captured_at).toLocaleString() : '';
    const src = e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noreferrer">${esc(e.source)}</a>` : esc(e.source);
    const pct = Math.round((e.score||0)*100);
    return `<div class="ev kind-${k}"><div class="rail"></div><div class="body">
      <div class="content">${KIND_ICON[k]||'•'} ${esc(e.content)}</div>
      <div class="meta">${when}${src? ' · '+src : ''}</div></div>
      <div class="relev" title="relevance ${pct}%"><div class="bar"><span style="width:${pct}%"></span></div>${pct}%</div></div>`;
  }).join('');
  return `<div class="evidence"><h4>Evidence · ${shown.length} matching ${shown.length===1?'memory':'memories'}</h4>${rows}</div>`;
}

async function ask(text){
  addUser(text); $('#hero').style.display='none';
  const bubble = addAI().querySelector('.bubble');
  send.disabled = true;
  try {
    const r = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({question: text})});
    const j = await r.json();
    if(j.error){ bubble.innerHTML = '⚠️ ' + esc(j.error); }
    else {
      bubble.innerHTML = esc(j.answer)
        + `<div class="engine">answered by ${esc(j.engine)}</div>`
        + renderEvidence(j.evidence);
    }
  } catch(e){ bubble.textContent = 'Request failed: ' + e; }
  send.disabled = false; scroll();
}
function scroll(){ window.scrollTo(0, document.body.scrollHeight); }
function go(){ const t = input.value.trim(); if(!t) return; input.value=''; ask(t); }
send.onclick = go;
input.addEventListener('keydown', e => { if(e.key==='Enter') go(); });
document.querySelectorAll('.chip').forEach(c => c.onclick = () => ask(c.textContent));
</script>
</body>
</html>
"""
