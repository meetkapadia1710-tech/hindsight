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
    /* Material dark-theme background: never pure black — Material explicitly
       recommends #121212 so elevation shadows stay visible and to avoid the
       visual vibration of white-on-black. */
    --bg: #121212;
    /* Elevation overlay tints (surface lightens as it "rises" toward the light,
       per Material's dark-theme elevation system) */
    --surface-00: #121212;  /* body */
    --surface-01: #1e1e1e;  /* resting cards: bubbles, evidence rows */
    --surface-02: #222222;
    --surface-03: #242424;
    --surface-04: #272727;  /* app bar */
    --surface-06: #2c2c2c;
    --surface-08: #2e2e2e;  /* raised: focused input, dialog */
    --surface-12: #333333;
    --surface-16: #353535;  /* dialog scrim content */
    /* Palette — MUI's real dark-theme defaults */
    --primary: #90caf9;       /* blue[200] */
    --primary-on: rgba(0,0,0,.87);   /* dark text on light-blue fill, per contrast rules */
    --secondary: #ce93d8;     /* purple[200] — user avatar, secondary accents only */
    --error: #f44336;
    --success: #66bb6a;
    /* Material dark-theme text emphasis levels (exact MUI constants) */
    --text-primary: rgba(255,255,255,.87);
    --text-secondary: rgba(255,255,255,.60);
    --text-disabled: rgba(255,255,255,.38);
    --divider: rgba(255,255,255,.12);
    /* Kind colors — used only as a small dot, not a rail */
    --k-browser: #66bb6a; --k-window: #90caf9; --k-clip: #ffb74d; --k-ocr: #f06292;
    /* Material shape scale: default 4px everywhere; pill only for chips */
    --radius: 4px;
    --radius-chip: 16px;
    /* Elevation: standard Material triple-layered shadow (umbra/penumbra/ambient) */
    --elevation-1: 0px 2px 1px -1px rgba(0,0,0,.2), 0px 1px 1px 0px rgba(0,0,0,.14), 0px 1px 3px 0px rgba(0,0,0,.12);
    --elevation-2: 0px 3px 1px -2px rgba(0,0,0,.2), 0px 2px 2px 0px rgba(0,0,0,.14), 0px 1px 5px 0px rgba(0,0,0,.12);
    --elevation-4: 0px 2px 4px -1px rgba(0,0,0,.2), 0px 4px 5px 0px rgba(0,0,0,.14), 0px 1px 10px 0px rgba(0,0,0,.12);
    --elevation-4-up: 0px -2px 4px -1px rgba(0,0,0,.2), 0px -4px 5px 0px rgba(0,0,0,.14), 0px -1px 10px 0px rgba(0,0,0,.12);
    --elevation-8: 0px 5px 5px -3px rgba(0,0,0,.2), 0px 8px 10px 1px rgba(0,0,0,.14), 0px 3px 14px 2px rgba(0,0,0,.12);
    --elevation-24: 0px 11px 15px -7px rgba(0,0,0,.2), 0px 24px 38px 3px rgba(0,0,0,.14), 0px 9px 46px 8px rgba(0,0,0,.12);
    --font: Roboto, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text-primary);
    font: 400 14px/1.5 var(--font); min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* -- ripple: Material's signature interaction -------------------------- */
  .ripple-host { position: relative; overflow: hidden; }
  .ripple { position: absolute; border-radius: 50%; background: currentColor; opacity: .25;
    transform: scale(0); animation: ripple-anim .5s ease-out; pointer-events: none; }
  @keyframes ripple-anim { to { transform: scale(1); opacity: 0; } }

  /* -- app bar ------------------------------------------------------------ */
  header {
    display: flex; align-items: center; gap: 16px; height: 64px; padding: 0 24px;
    background: var(--surface-04); box-shadow: var(--elevation-4); overflow: hidden;
    position: sticky; top: 0; z-index: 10;
  }
  .logo { font-size: 20px; font-weight: 500; color: var(--text-primary); flex: none; white-space: nowrap; }
  .logo span { color: var(--primary); }
  .tag { color: var(--text-secondary); font-size: 13px; white-space: nowrap; }
  .hstats { margin-left: auto; color: var(--text-secondary); font-size: 13px; white-space: nowrap; }
  @media (max-width: 760px) { .tag { display: none; } }
  @media (max-width: 560px) { .hstats { display: none; } }

  /* -- text button (forget all) ------------------------------------------- */
  .btn-text {
    background: transparent; border: none; color: var(--primary);
    font: 500 14px/1 var(--font); letter-spacing: .02857em; text-transform: uppercase;
    padding: 8px 12px; border-radius: var(--radius); cursor: pointer;
    display: inline-flex; align-items: center; gap: 8px; flex: none; white-space: nowrap;
    transition: background-color .15s;
  }
  .btn-text:hover { background: rgba(244,67,54,.08); color: var(--error); }
  .btn-text:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .ic { flex: none; }

  /* -- status chip --------------------------------------------------------- */
  .chip-status {
    display: inline-flex; align-items: center; gap: 8px; height: 32px; flex: none;
    padding: 0 12px; border-radius: var(--radius-chip); background: var(--surface-02);
    color: var(--text-secondary); font-size: 13px; white-space: nowrap;
  }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); flex: none; }
  .status-dot.off { background: var(--error); }

  main { max-width: 760px; margin: 0 auto; padding: 32px 24px 112px; }

  /* -- hero (h5 / subtitle1) ------------------------------------------------ */
  .hero { text-align: center; padding: 48px 0 8px; }
  .hero h1 { font: 500 24px/1.3 var(--font); color: var(--text-primary); margin: 0 0 8px; }
  .hero p { font: 400 16px/1.5 var(--font); color: var(--text-secondary); margin: 0; }

  /* -- suggestion chips ----------------------------------------------------- */
  .chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 24px; }
  .chip {
    display: inline-flex; align-items: center; height: 32px; padding: 0 16px;
    border-radius: var(--radius-chip); border: 1px solid var(--divider);
    background: var(--surface-02); color: var(--text-primary);
    font: 500 14px/1 var(--font); letter-spacing: .02857em;
    cursor: pointer; transition: background-color .15s, border-color .15s;
  }
  .chip:hover { background: var(--surface-04); border-color: var(--text-secondary); }
  .chip:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }

  /* -- thread / avatars / cards --------------------------------------------- */
  .thread { display: flex; flex-direction: column; gap: 24px; margin-top: 8px; }
  .msg { display: flex; gap: 12px; }
  .msg .who { width: 32px; height: 32px; border-radius: 50%; flex: none;
    display: grid; place-items: center; font: 500 14px/1 var(--font); }
  .msg.user .who { background: var(--secondary); color: var(--primary-on); }
  .msg.ai .who { background: var(--primary); color: var(--primary-on); }
  .bubble { background: var(--surface-01); box-shadow: var(--elevation-1);
    border-radius: var(--radius); padding: 16px; flex: 1; white-space: pre-wrap;
    font: 400 16px/1.5 var(--font); color: var(--text-primary); }
  .msg.user .bubble { background: var(--surface-03); box-shadow: none; }
  .engine { font: 400 12px/1.4 var(--font); color: var(--text-secondary); margin-top: 12px; }

  /* -- evidence: dense list -------------------------------------------------- */
  .evidence { margin-top: 16px; padding-top: 8px; border-top: 1px solid var(--divider); }
  .evidence h4 { margin: 0 0 4px; font: 500 10px/2 var(--font); text-transform: uppercase;
    letter-spacing: 1.5px; color: var(--text-secondary); }
  .ev { display: flex; align-items: flex-start; gap: 12px; padding: 8px;
    border-bottom: 1px solid var(--divider); cursor: default; transition: background-color .15s; }
  .ev:last-child { border-bottom: 0; }
  .ev:hover { background: rgba(255,255,255,.04); }
  .ev .body { flex: 1; min-width: 0; }
  .ev .content { font: 400 14px/1.5 var(--font); color: var(--text-primary); }
  .ev .meta { font: 400 12px/1.4 var(--font); color: var(--text-secondary); margin-top: 4px;
    word-break: break-word; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .kdot { width: 8px; height: 8px; border-radius: 50%; flex: none; display: inline-block; }
  .kdot.k-browser { background: var(--k-browser); }
  .kdot.k-window { background: var(--k-window); }
  .kdot.k-clipboard { background: var(--k-clip); }
  .kdot.k-ocr { background: var(--k-ocr); }
  .kind-label { font: 500 10px/1 var(--font); text-transform: uppercase; letter-spacing: 1px;
    color: var(--text-secondary); }
  .ev .relev { flex: none; align-self: center; display: flex; align-items: center; gap: 8px;
    font: 400 11px/1 var(--font); color: var(--text-secondary); }
  .ev .relev .bar { width: 48px; height: 4px; border-radius: 2px; background: rgba(255,255,255,.12);
    overflow: hidden; }
  .ev .relev .bar > span { display: block; height: 100%; background: var(--primary); }

  /* -- composer: outlined text field + contained button --------------------- */
  .composer { position: fixed; left: 0; right: 0; bottom: 0;
    background: var(--surface-04); box-shadow: var(--elevation-4-up); padding: 16px 24px; z-index: 8; }
  .composer .box { max-width: 760px; margin: 0 auto; display: flex; gap: 16px; align-items: center; }
  .field { flex: 1; display: flex; align-items: center; background: var(--surface-02);
    border: 1px solid var(--divider); border-radius: var(--radius);
    transition: border-color .15s, box-shadow .15s; }
  .field:focus-within { border-color: var(--primary); box-shadow: 0 0 0 1px var(--primary); }
  input[type=text] { flex: 1; background: transparent; border: none; outline: none;
    padding: 16px; color: var(--text-primary); font: 400 16px/1.4 var(--font); }
  input[type=text]::placeholder { color: var(--text-disabled); }
  .send { height: 48px; padding: 0 24px; border: none; border-radius: var(--radius);
    background: var(--primary); color: var(--primary-on);
    font: 500 14px/1 var(--font); letter-spacing: .02857em; text-transform: uppercase;
    display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
    box-shadow: var(--elevation-2); transition: box-shadow .15s, filter .15s; }
  .send:hover { box-shadow: var(--elevation-4); filter: brightness(1.08); }
  .send:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .send:disabled { background: rgba(255,255,255,.12); color: var(--text-disabled);
    box-shadow: none; cursor: default; filter: none; }

  /* -- circular indeterminate progress (SVG arc, not a two-tone border) ----- */
  .spin { width: 20px; height: 20px; animation: m-rotate 1.4s linear infinite; }
  .spin circle { fill: none; stroke: var(--primary); stroke-width: 2.5; stroke-linecap: round;
    stroke-dasharray: 1, 200; stroke-dashoffset: 0; animation: m-dash 1.4s ease-in-out infinite; }
  @keyframes m-rotate { 100% { transform: rotate(360deg); } }
  @keyframes m-dash {
    0%   { stroke-dasharray: 1, 200; stroke-dashoffset: 0; }
    50%  { stroke-dasharray: 44, 200; stroke-dashoffset: -15; }
    100% { stroke-dasharray: 44, 200; stroke-dashoffset: -59; }
  }

  /* -- dialog (replaces native confirm() for Forget all) --------------------- */
  .m-scrim { position: fixed; inset: 0; background: rgba(0,0,0,.5);
    display: flex; align-items: center; justify-content: center; z-index: 50;
    animation: scrim-in .15s ease-out; }
  @keyframes scrim-in { from { opacity: 0; } to { opacity: 1; } }
  .m-dialog { width: min(400px, calc(100vw - 48px)); background: var(--surface-16);
    border-radius: var(--radius); box-shadow: var(--elevation-24); padding: 24px;
    animation: dialog-in .15s ease-out; }
  @keyframes dialog-in { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }
  .m-dialog-title { font: 500 20px/1.3 var(--font); color: var(--text-primary); margin-bottom: 12px; }
  .m-dialog-body { font: 400 14px/1.6 var(--font); color: var(--text-secondary); margin-bottom: 24px; }
  .m-dialog-actions { display: flex; justify-content: flex-end; gap: 8px; }
  .m-text-btn { background: transparent; border: none; padding: 8px 12px; border-radius: var(--radius);
    color: var(--primary); font: 500 14px/1 var(--font); letter-spacing: .02857em; text-transform: uppercase;
    cursor: pointer; transition: background-color .15s; }
  .m-text-btn:hover { background: rgba(144,202,249,.08); }
  .m-text-btn:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .m-text-btn-error { color: var(--error); }
  .m-text-btn-error:hover { background: rgba(244,67,54,.08); }

  a { color: var(--primary); text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<header>
  <div class="logo">Hind<span>sight</span></div>
  <div class="tag">your PC's memory · stays on your PC</div>
  <div class="hstats" id="hstats"></div>
  <button class="btn-text ripple-host" id="forget" title="Permanently delete every stored memory">
    <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
    Forget all
  </button>
  <div class="chip-status" id="badge"><span class="status-dot" id="dot"></span><span id="badgetext">checking…</span></div>
</header>
<main>
  <div class="hero" id="hero">
    <h1>Ask your past.</h1>
    <p>Everything you've seen, copied, and read — searchable, and 100% local.</p>
    <div class="chips" id="chips">
      <div class="chip ripple-host">What was I working on this morning?</div>
      <div class="chip ripple-host">What articles did I read about embeddings?</div>
      <div class="chip ripple-host">What did I copy to my clipboard earlier?</div>
      <div class="chip ripple-host">Which GitHub repos did I look at today?</div>
    </div>
  </div>
  <div class="thread" id="thread"></div>
</main>
<div class="composer">
  <div class="box">
    <div class="field">
      <input id="q" type="text" placeholder="Ask about anything you've done on this machine…" autocomplete="off" />
    </div>
    <button class="send ripple-host" id="send">
      <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
      Recall
    </button>
  </div>
</div>
<script>
const $ = s => document.querySelector(s);
const thread = $('#thread'), input = $('#q'), send = $('#send');

function ripple(el, evt){
  const r = document.createElement('span');
  r.className = 'ripple';
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height) * 2;
  r.style.width = r.style.height = size + 'px';
  r.style.left = (evt.clientX - rect.left - size/2) + 'px';
  r.style.top  = (evt.clientY - rect.top  - size/2) + 'px';
  el.appendChild(r);
  r.addEventListener('animationend', () => r.remove());
}
function wireRipples(root){
  root.querySelectorAll('.ripple-host').forEach(el => {
    el.addEventListener('click', e => ripple(el, e));
  });
}

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

function esc(s){ return (s||'').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

// Material Dialog — replaces native confirm() for "Forget all". The gate
// (destructive call only fires if the user picks the confirm action) is
// identical to a plain confirm(); only the chrome is a real Material dialog.
function materialConfirm(title, message, confirmLabel, cancelLabel){
  return new Promise(resolve => {
    const scrim = document.createElement('div'); scrim.className = 'm-scrim';
    scrim.innerHTML = `<div class="m-dialog" role="alertdialog" aria-modal="true">
      <div class="m-dialog-title">${esc(title)}</div>
      <div class="m-dialog-body">${esc(message)}</div>
      <div class="m-dialog-actions">
        <button class="m-text-btn ripple-host" data-a="cancel">${esc(cancelLabel)}</button>
        <button class="m-text-btn m-text-btn-error ripple-host" data-a="confirm">${esc(confirmLabel)}</button>
      </div></div>`;
    document.body.appendChild(scrim);
    wireRipples(scrim);
    function close(result){ scrim.remove(); document.removeEventListener('keydown', onKey); resolve(result); }
    function onKey(e){ if (e.key === 'Escape') close(false); }
    document.addEventListener('keydown', onKey);
    scrim.addEventListener('click', e => {
      if (e.target === scrim) return close(false);
      const a = e.target.closest('[data-a]');
      if (!a) return;
      close(a.dataset.a === 'confirm');
    });
  });
}

$('#forget').addEventListener('click', async (e) => {
  ripple($('#forget'), e);
  const ok = await materialConfirm(
    'Forget everything?',
    'This permanently deletes every stored memory. This cannot be undone.',
    'Delete', 'Cancel'
  );
  if (!ok) return;
  await fetch('/api/forget_all', {method:'POST'});
  thread.innerHTML=''; $('#hero').style.display='';
  refreshStats();
});

const KIND_LABEL = { clipboard:'Clipboard', window:'Window', browser:'Browser', ocr:'OCR' };

function addUser(text){
  const el = document.createElement('div'); el.className = 'msg user';
  el.innerHTML = `<div class="who">Y</div><div class="bubble">${esc(text)}</div>`;
  thread.appendChild(el); scroll();
}
function addAI(){
  const el = document.createElement('div'); el.className = 'msg ai';
  el.innerHTML = `<div class="who">H</div><div class="bubble"><svg class="spin" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8"></circle></svg></div>`;
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
    return `<div class="ev ripple-host"><div class="body">
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
      wireRipples(bubble);
    }
  } catch(e){ bubble.textContent = 'Request failed: ' + e; }
  send.disabled = false; scroll();
}
function scroll(){ window.scrollTo(0, document.body.scrollHeight); }
function go(){ const t = input.value.trim(); if(!t) return; input.value=''; ask(t); }
send.addEventListener('click', (e) => { ripple(send, e); go(); });
input.addEventListener('keydown', e => { if(e.key==='Enter') go(); });
document.querySelectorAll('.chip').forEach(c => c.addEventListener('click', (e) => { ripple(c, e); ask(c.textContent); }));
</script>
</body>
</html>
"""
