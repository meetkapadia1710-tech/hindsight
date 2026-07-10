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
    --bg: #0a0b0d; --surface: #131518; --surface-2: #17191d;
    --border: #23262b; --text: #eaecef; --text-muted: #878d97; --text-faint: #5c6169;
    --accent: #6b8cff; --good: #34c98e; --bad: #e5555f;
    --k-browser: #34c98e; --k-window: #6b8cff; --k-clip: #e0a952; --k-ocr: #d97bb0;
    --font-serif: Georgia, "Iowan Old Style", "Times New Roman", serif;
    --font-sans: -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font: 15px/1.6 var(--font-sans); min-height: 100vh;
  }
  header {
    display: flex; align-items: center; gap: 16px; padding: 16px 24px;
    border-bottom: 1px solid var(--border); position: sticky; top: 0;
    background: var(--bg); z-index: 5;
  }
  .logo { font-family: var(--font-serif); font-size: 21px; font-weight: 600; letter-spacing: -.01em; }
  .logo span { color: var(--accent); }
  .tag { color: var(--text-muted); font-size: 12.5px; }
  .hstats { margin-left: auto; color: var(--text-muted); font-size: 12.5px; }
  .forget {
    background: transparent; border: 1px solid var(--border); color: var(--text-muted);
    border-radius: 8px; padding: 6px 12px; font-size: 12.5px; cursor: pointer;
    font-family: var(--font-sans); transition: border-color .14s ease-out, color .14s ease-out;
  }
  .forget:hover { border-color: var(--bad); color: var(--bad); }
  .badge {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 12px; border: 1px solid var(--border); border-radius: 8px;
    font-size: 12.5px; color: var(--text-muted);
  }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good); flex: none; }
  .dot.off { background: var(--bad); }
  main { max-width: 760px; margin: 0 auto; padding: 32px 24px 140px; }
  .hero { text-align: center; margin: 32px 0 24px; }
  .hero h1 { font-family: var(--font-serif); font-weight: 600; font-size: 28px;
    margin: 0 0 8px; letter-spacing: -.01em; }
  .hero p { color: var(--text-muted); margin: 0; font-size: 14.5px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
    margin-top: 16px; }
  .chip { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px;
    background: var(--surface); color: var(--text); cursor: pointer; font-size: 13.5px;
    transition: border-color .14s ease-out, background .14s ease-out; }
  .chip:hover { border-color: var(--accent); background: var(--surface-2); }
  .thread { display: flex; flex-direction: column; gap: 24px; margin-top: 8px; }
  .msg { display: flex; gap: 12px; }
  .msg .who { width: 30px; height: 30px; border-radius: 8px; flex: none;
    display: grid; place-items: center; font-size: 13px; font-weight: 700;
    font-family: var(--font-sans); }
  .msg.user .who { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
  .msg.ai .who { background: var(--accent); color: #0a0b0d; }
  .bubble { background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; flex: 1; white-space: pre-wrap;
    font-size: 14.5px; line-height: 1.6; }
  .msg.user .bubble { background: var(--surface-2); }
  .engine { font-size: 11.5px; color: var(--text-faint); margin-top: 10px; }
  .evidence { margin-top: 14px; border-top: 1px solid var(--border); padding-top: 12px; }
  .evidence h4 { margin: 0 0 10px; font-size: 11px; text-transform: uppercase;
    letter-spacing: .08em; color: var(--text-faint); font-weight: 600; }
  .ev { display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .ev:last-child { border-bottom: 0; }
  .ev .body { flex: 1; min-width: 0; }
  .ev .content { font-size: 13.5px; color: var(--text); }
  .ev .meta { font-size: 11.5px; color: var(--text-faint); margin-top: 4px;
    word-break: break-word; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .kdot { width: 6px; height: 6px; border-radius: 50%; flex: none; display: inline-block; }
  .kdot.k-browser { background: var(--k-browser); }
  .kdot.k-window { background: var(--k-window); }
  .kdot.k-clipboard { background: var(--k-clip); }
  .kdot.k-ocr { background: var(--k-ocr); }
  .kind-label { text-transform: uppercase; letter-spacing: .05em; font-size: 10.5px; color: var(--text-faint); }
  .ev .relev { flex: none; align-self: center; display: flex; align-items: center; gap: 8px;
    font-size: 11px; color: var(--text-faint); }
  .ev .relev .bar { width: 48px; height: 4px; border-radius: 2px; background: var(--surface-2);
    overflow: hidden; }
  .ev .relev .bar > span { display: block; height: 100%; border-radius: 2px; background: var(--accent); }
  .composer { position: fixed; bottom: 0; left: 0; right: 0;
    background: var(--surface-2); border-top: 1px solid var(--border); padding: 16px 24px; }
  .composer .box { max-width: 760px; margin: 0 auto; display: flex; gap: 8px; }
  input[type=text] { flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px; color: var(--text); font-size: 14.5px;
    font-family: var(--font-sans); outline: none;
    transition: border-color .14s ease-out, box-shadow .14s ease-out; }
  input[type=text]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(107,140,255,.15); }
  button.send { background: var(--accent); border: 0; color: #0a0b0d; font-weight: 600;
    padding: 0 24px; border-radius: 10px; cursor: pointer; font-size: 14.5px;
    font-family: var(--font-sans); transition: opacity .14s ease-out; }
  button.send:hover { opacity: .92; }
  button.send:disabled { opacity: .5; cursor: default; }
  .spin { display: inline-block; width: 14px; height: 14px; border: 2px solid var(--border);
    border-top-color: var(--text-muted); border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
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

const KIND_LABEL = { clipboard:'Clipboard', window:'Window', browser:'Browser', ocr:'OCR' };
function esc(s){ return (s||'').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

function addUser(text){
  const el = document.createElement('div'); el.className = 'msg user';
  el.innerHTML = `<div class="who">Y</div><div class="bubble">${esc(text)}</div>`;
  thread.appendChild(el); scroll();
}
function addAI(){
  const el = document.createElement('div'); el.className = 'msg ai';
  el.innerHTML = `<div class="who">H</div><div class="bubble"><span class="spin"></span></div>`;
  thread.appendChild(el); scroll(); return el;
}
function renderEvidence(ev){
  if(!ev || !ev.length) return '';
  // Keep the clearly-relevant matches: within 0.15 of the best score, max 5.
  const top = ev[0].score || 0;
  const shown = ev.filter(e => (e.score||0) >= top - 0.15).slice(0,5);
  const rows = shown.map(e => {
    const k = e.kind || 'window';
    const label = KIND_LABEL[k] || k;
    const when = e.captured_at ? new Date(e.captured_at).toLocaleString() : '';
    const src = e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noreferrer">${esc(e.source)}</a>` : esc(e.source);
    const pct = Math.round((e.score||0)*100);
    return `<div class="ev"><div class="body">
      <div class="content">${esc(e.content)}</div>
      <div class="meta"><span class="kdot k-${k}"></span><span class="kind-label">${label}</span> · ${when}${src? ' · '+src : ''}</div></div>
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
    if(j.error){ bubble.innerHTML = 'Error: ' + esc(j.error); }
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
