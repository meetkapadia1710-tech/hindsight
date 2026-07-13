"""The single-page UI, inlined so the app is one importable module with no
static-file plumbing. Vanilla JS, no build step, no external requests."""

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
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
    font: 400 14px/1.5 var(--font); min-height: 100vh; min-height: 100dvh;
    overflow-x: clip;   /* long URLs / off-canvas panels never scroll the page sideways */
    -webkit-font-smoothing: antialiased;
  }

  /* -- ripple: Material's signature interaction -------------------------- */
  .ripple-host { position: relative; overflow: hidden; }
  .ripple { position: absolute; border-radius: 50%; background: currentColor; opacity: .25;
    transform: scale(0); animation: ripple-anim .5s ease-out; pointer-events: none; }
  @keyframes ripple-anim { to { transform: scale(1); opacity: 0; } }

  /* -- state layers: hover/focus/pressed tint every interactive surface -- */
  .state-layer { position: relative; }
  .state-layer::after { content: ''; position: absolute; inset: 0; border-radius: inherit;
    background: currentColor; opacity: 0; transition: opacity 100ms; pointer-events: none; }
  .state-layer:hover::after      { opacity: .08; }
  .state-layer:focus-visible::after,
  .state-layer:active::after     { opacity: .12; }

  @media (prefers-reduced-motion: reduce) {
    .ripple, .spin, .spin circle, .live-item.fresh, .live-head .rec { animation: none !important; }
    .live-drawer { transition: none !important; }
  }

  /* -- app bar: flush at rest, elevates once content scrolls under it ----- */
  header {
    display: flex; align-items: center; gap: 16px; height: 64px; padding: 0 24px;
    background: var(--surface-04); box-shadow: none; overflow: hidden;
    position: sticky; top: 0; z-index: 10; transition: box-shadow 150ms;
  }
  header.raised { box-shadow: var(--elevation-4); }
  .logo { font-size: 20px; font-weight: 500; color: var(--text-primary); flex: none; white-space: nowrap; }
  .logo span { color: var(--primary); }
  .tag { color: var(--text-secondary); font-size: 13px; white-space: nowrap; }
  .hstats { margin-left: auto; color: var(--text-secondary); font-size: 13px; white-space: nowrap; }
  @media (max-width: 600px) { .tag { display: none; } }

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
  /* icon button (app-bar overflow) */
  .btn-icon { background: transparent; border: none; color: var(--text-secondary); cursor: pointer;
    width: 44px; height: 44px; border-radius: 50%; display: none; flex: none;
    align-items: center; justify-content: center; transition: background-color .15s; }
  .btn-icon:hover { background: rgba(255,255,255,.08); color: var(--text-primary); }
  .btn-icon:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .appbar-more { margin-left: 0; }
  /* overflow menu */
  .menu { position: fixed; top: 56px; right: 8px; min-width: 200px; z-index: 40;
    background: var(--surface-08); box-shadow: var(--elevation-8); border-radius: var(--radius);
    padding: 8px 0; display: none; }
  .menu.open { display: block; }
  .menu-item { width: 100%; background: transparent; border: none; cursor: pointer;
    display: flex; align-items: center; gap: 16px; padding: 0 16px; height: 48px;
    color: var(--text-primary); font: 400 15px/1 var(--font); text-align: left; }
  .menu-item .ic { color: var(--text-secondary); }
  .menu-item:focus-visible { outline: 2px solid var(--primary); outline-offset: -2px; }
  .menu-item-error, .menu-item-error .ic { color: var(--error); }

  /* -- status chip --------------------------------------------------------- */
  .chip-status {
    display: inline-flex; align-items: center; gap: 8px; height: 32px; flex: none;
    padding: 0 12px; border-radius: var(--radius-chip); background: var(--surface-02);
    color: var(--text-secondary); font-size: 13px; white-space: nowrap;
  }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); flex: none; }
  .status-dot.off { background: var(--error); }

  main { max-width: 760px; margin: 0 auto; padding: 32px 24px 156px; }

  /* -- hero (h5 / subtitle1) ------------------------------------------------ */
  .hero { text-align: center; padding: 48px 0 8px; }
  .hero h1 { font-weight: 500; font-size: clamp(1.35rem, 4vw + .5rem, 1.5rem); line-height: 1.3;
    color: var(--text-primary); margin: 0 0 8px; }
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
  .digest-row { display: flex; justify-content: center; margin-top: 16px; }
  .digest-chip { display: inline-flex; align-items: center; gap: 8px; height: 36px; padding: 0 20px;
    border-radius: var(--radius-chip); border: 1px solid var(--primary);
    background: rgba(144,202,249,.12); color: var(--primary);
    font: 500 14px/1 var(--font); letter-spacing: .02857em; cursor: pointer;
    transition: background-color .15s; }
  .digest-chip:hover { background: rgba(144,202,249,.22); }
  .digest-chip:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }

  /* -- thread / avatars / cards --------------------------------------------- */
  .thread { display: flex; flex-direction: column; gap: 24px; margin-top: 8px; }
  .msg { display: flex; gap: 12px; }
  .msg .who { width: 32px; height: 32px; border-radius: 50%; flex: none;
    display: grid; place-items: center; font: 500 14px/1 var(--font); }
  .msg.user .who { background: var(--secondary); color: var(--primary-on); }
  .msg.ai .who { background: var(--primary); color: var(--primary-on); }
  .bubble { background: var(--surface-01); box-shadow: var(--elevation-1);
    border-radius: var(--radius); padding: 16px; flex: 1; min-width: 0; white-space: pre-wrap;
    overflow-wrap: anywhere; font: 400 16px/1.5 var(--font); color: var(--text-primary); }
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
  .ev:focus-visible { outline: 2px solid var(--primary); outline-offset: -2px; }
  .ev .body { flex: 1; min-width: 0; }
  .ev .content { font: 400 14px/1.5 var(--font); color: var(--text-primary); overflow-wrap: anywhere; }
  .ev .meta { font: 400 12px/1.4 var(--font); color: var(--text-secondary); margin-top: 4px;
    overflow-wrap: anywhere; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .ev .meta a { overflow-wrap: anywhere; }
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

  /* -- composer: outlined text field w/ floating label + contained button -- */
  .composer { position: fixed; left: 0; right: 0; bottom: 0;
    background: var(--surface-04); box-shadow: var(--elevation-4-up); z-index: 8;
    padding: 16px 24px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
  .composer .box { max-width: 760px; margin: 0 auto; display: flex; gap: 16px; align-items: center; }
  .field { position: relative; flex: 1; display: flex; align-items: center; background: var(--surface-02);
    border: 1px solid var(--divider); border-radius: var(--radius);
    transition: border-color .15s, box-shadow .15s; }
  .field:focus-within { border-color: var(--primary); box-shadow: 0 0 0 1px var(--primary); }
  input[type=text] { flex: 1; background: transparent; border: none; outline: none;
    padding: 16px; color: var(--text-primary); font: 400 16px/1.4 var(--font); }
  input[type=text]::placeholder { color: transparent; }
  .field label {
    position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
    font: 400 16px/1.4 var(--font); color: var(--text-disabled);
    background: var(--surface-02); padding: 0 4px; margin-left: -4px;
    pointer-events: none; transition: top 150ms, font-size 150ms, color 150ms;
  }
  input[type=text]:focus ~ label,
  input[type=text]:not(:placeholder-shown) ~ label {
    top: 0; font-size: 12px; color: var(--primary);
  }
  .send { height: 48px; padding: 0 24px; border: none; border-radius: var(--radius);
    background: var(--primary); color: var(--primary-on);
    font: 500 14px/1 var(--font); letter-spacing: .02857em; text-transform: uppercase;
    display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
    box-shadow: var(--elevation-2); transition: box-shadow .15s, filter .15s; }
  .send:hover { box-shadow: var(--elevation-4); filter: brightness(1.08); }
  .send:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .send:disabled { background: rgba(255,255,255,.12); color: var(--text-disabled);
    box-shadow: none; cursor: default; filter: none; }

  /* -- time-scope filter chips --------------------------------------------- */
  .scopes { gap: 6px; justify-content: flex-start; flex-wrap: wrap; margin-bottom: 8px; }
  .scope-chip { height: 28px; padding: 0 12px; border-radius: var(--radius-chip);
    border: 1px solid var(--divider); background: transparent; color: var(--text-secondary);
    font: 500 12px/1 var(--font); letter-spacing: .02em; cursor: pointer;
    display: inline-flex; align-items: center;
    transition: background-color .15s, border-color .15s, color .15s; }
  .scope-chip:hover { border-color: var(--text-secondary); color: var(--text-primary); }
  .scope-chip.active { background: rgba(144,202,249,.16); border-color: var(--primary); color: var(--primary); }
  .scope-chip:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
  .scope-tag { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px;
    font: 500 10px/1 var(--font); text-transform: uppercase; letter-spacing: 1px; color: var(--primary); }
  .scope-tag .kdot { background: var(--primary); }

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

  /* -- live capture drawer -------------------------------------------------- */
  .live-drawer { position: fixed; top: 64px; right: 0; bottom: 124px; width: 340px; max-width: 92vw;
    background: var(--surface-02); box-shadow: var(--elevation-8); z-index: 9;
    display: flex; flex-direction: column;
    transform: translateX(100%); transition: transform 200ms ease-out; }
  .live-drawer.open { transform: translateX(0); }
  .sheet-scrim { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 8; display: none; }
  .sheet-handle { display: none; }
  .live-head { display: flex; align-items: center; gap: 10px; padding: 16px;
    border-bottom: 1px solid var(--divider); flex: none; }
  .live-head .rec { width: 8px; height: 8px; border-radius: 50%; background: var(--error);
    flex: none; animation: rec-pulse 1.6s ease-in-out infinite; }
  .live-head .rec.paused { background: var(--text-disabled); animation: none; }
  @keyframes rec-pulse { 0%,100% { opacity: 1; } 50% { opacity: .25; } }
  .live-title { font: 500 14px/1 var(--font); letter-spacing: .02857em;
    text-transform: uppercase; color: var(--text-primary); }
  .live-sub { font: 400 11px/1.3 var(--font); color: var(--text-secondary); margin-top: 2px; }
  .live-close { margin-left: auto; background: transparent; border: none; color: var(--text-secondary);
    cursor: pointer; border-radius: var(--radius); padding: 6px; display: inline-flex; }
  .live-close:hover { background: rgba(255,255,255,.08); color: var(--text-primary); }
  .live-list { flex: 1; overflow-y: auto; padding: 8px; }
  .live-empty { color: var(--text-secondary); font-size: 13px; text-align: center; padding: 24px 12px; }
  .live-item { padding: 12px; border-radius: var(--radius); background: var(--surface-01);
    margin-bottom: 8px; }
  .live-item .lc { font: 400 13px/1.4 var(--font); color: var(--text-primary);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .live-item .lm { font: 400 11px/1 var(--font); color: var(--text-secondary); margin-top: 6px;
    display: flex; align-items: center; gap: 6px; }
  .live-item.fresh { animation: flash-in .6s ease-out; }
  @keyframes flash-in {
    from { opacity: 0; transform: translateY(-6px); box-shadow: 0 0 0 2px var(--primary); }
    to   { opacity: 1; transform: translateY(0); box-shadow: none; }
  }

  /* -- privacy panel (reuses the .live-drawer shell) ------------------------ */
  .priv-body { flex: 1; overflow-y: auto; padding: 16px; }
  .priv-pause { display: flex; align-items: center; gap: 12px; padding: 16px;
    border-radius: var(--radius); background: var(--surface-01); box-shadow: var(--elevation-1);
    margin-bottom: 20px; }
  .priv-pause .grow { flex: 1; }
  .priv-status { font: 500 15px/1.2 var(--font); color: var(--success); }
  .priv-status.paused { color: var(--error); }
  .priv-section-title { font: 500 10px/1 var(--font); text-transform: uppercase;
    letter-spacing: 1.5px; color: var(--text-secondary); margin: 4px 0 8px; }
  .priv-row { display: flex; align-items: center; gap: 12px; padding: 10px 4px; }
  .priv-row .grow { flex: 1; font: 400 14px/1.3 var(--font); color: var(--text-primary); }
  .priv-row .sub { font: 400 11px/1.2 var(--font); color: var(--text-secondary); margin-top: 2px; }
  .priv-divider { height: 1px; background: var(--divider); margin: 16px 0; }
  /* Material switch */
  .switch { position: relative; width: 36px; height: 20px; flex: none; display: inline-block; }
  .switch input { position: absolute; opacity: 0; width: 100%; height: 100%; margin: 0; cursor: pointer; z-index: 2; }
  .switch .track { position: absolute; inset: 3px 0; border-radius: 8px; background: var(--surface-12);
    transition: background-color .15s; }
  .switch .thumb { position: absolute; top: 2px; left: 2px; width: 16px; height: 16px; border-radius: 50%;
    background: var(--text-secondary); transition: transform .15s, background-color .15s; box-shadow: var(--elevation-1); }
  .switch input:checked ~ .track { background: rgba(144,202,249,.5); }
  .switch input:checked ~ .thumb { transform: translateX(16px); background: var(--primary); }
  .switch input:focus-visible ~ .track { outline: 2px solid var(--primary); outline-offset: 2px; }
  .priv-excl-add { display: flex; gap: 8px; margin: 4px 0 12px; }
  .priv-excl-add input { flex: 1; background: var(--surface-02); border: 1px solid var(--divider);
    border-radius: var(--radius); padding: 10px 12px; color: var(--text-primary); font: 400 13px/1.2 var(--font); outline: none; }
  .priv-excl-add input:focus { border-color: var(--primary); box-shadow: 0 0 0 1px var(--primary); }
  .priv-excl-add button { border: none; border-radius: var(--radius); background: var(--primary);
    color: var(--primary-on); font: 500 13px/1 var(--font); text-transform: uppercase; letter-spacing: .02857em;
    padding: 0 14px; cursor: pointer; }
  .excl-chip { display: inline-flex; align-items: center; gap: 8px; padding: 6px 6px 6px 12px;
    border-radius: var(--radius-chip); background: var(--surface-03); color: var(--text-primary);
    font: 400 13px/1 var(--font); margin: 0 6px 6px 0; }
  .excl-chip button { background: transparent; border: none; color: var(--text-secondary); cursor: pointer;
    display: inline-flex; padding: 2px; border-radius: 50%; }
  .excl-chip button:hover { background: rgba(255,255,255,.1); color: var(--error); }
  .priv-empty { font: 400 12px/1.4 var(--font); color: var(--text-secondary); }
  /* per-evidence delete button */
  .ev-del { flex: none; align-self: center; background: transparent; border: none; cursor: pointer;
    color: var(--text-disabled); padding: 6px; border-radius: 50%; display: inline-flex;
    transition: background-color .12s, color .12s; }
  .ev:hover .ev-del { color: var(--text-secondary); }
  .ev-del:hover { background: rgba(244,67,54,.12); color: var(--error); }

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

  /* ===================== responsive: phone (max-width 599px) ============ */
  @media (max-width: 599px) {
    main { padding: 16px 16px 150px; }
    .hword-full { display: none; }

    /* app bar: collapse the text actions into an overflow menu */
    header { gap: 8px; padding: 0 8px 0 16px; }
    .appbar-action { display: none; }
    .btn-icon { display: inline-flex; }
    .chip-status { background: transparent; padding: 0 4px; gap: 4px; }
    #badgetext { display: none; }

    /* hero */
    .hero { padding: 24px 0 8px; }
    .hero p { font-size: 15px; }

    /* suggestion + scope chips become horizontal snap-scroll rows */
    .chips, .scopes {
      flex-wrap: nowrap; overflow-x: auto; justify-content: flex-start;
      scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; padding-bottom: 4px;
      -webkit-mask-image: linear-gradient(to right, #000 92%, transparent);
              mask-image: linear-gradient(to right, #000 92%, transparent);
    }
    .chips { margin-top: 20px; }
    .chips::-webkit-scrollbar, .scopes::-webkit-scrollbar { display: none; }
    .chips, .scopes { scrollbar-width: none; }
    .chip, .scope-chip { flex: none; scroll-snap-align: start; }

    /* thread */
    .msg { gap: 8px; }
    .msg .who { width: 28px; height: 28px; font-size: 12px; }
    .bubble { padding: 12px 14px; font-size: 15px; }

    /* evidence rows stack vertically: meta, then content, then a full-width bar */
    .ev { flex-direction: column; align-items: stretch; gap: 6px; padding: 12px 8px; position: relative; }
    .ev .body { display: flex; flex-direction: column; min-width: 0; }
    .ev .content { order: 2; }
    .ev .meta { order: 1; margin-top: 0; margin-bottom: 2px; padding-right: 44px; }
    .ev .relev { align-self: stretch; width: 100%; justify-content: flex-start; }
    .ev .relev .bar { flex: 1; width: auto; }
    .ev-del { position: absolute; top: 6px; right: 2px; align-self: auto; }

    /* composer: icon-only send */
    .composer .box { gap: 8px; }
    .send-label { display: none; }
    .send { width: 48px; padding: 0; justify-content: center; }

    /* dialogs */
    .m-dialog { width: min(calc(100vw - 32px), 560px); }
    .m-dialog-actions { flex-wrap: wrap; }

    /* live feed -> bottom sheet (scrim + drag handle) */
    .sheet-scrim.show { display: block; }
    .live-drawer { top: auto; left: 0; right: 0; bottom: 0; width: 100%; max-width: 100%;
      height: 80vh; height: 80dvh; border-radius: 16px 16px 0 0;
      transform: translateY(100%); transition: transform 220ms ease-out; }
    .live-drawer.open { transform: translateY(0); }
    .sheet-handle { display: block; width: 32px; height: 4px; border-radius: 2px;
      background: var(--text-disabled); margin: 8px auto 0; flex: none; cursor: pointer; }

    /* privacy panel -> full-screen dialog (covers the app bar, shows its own header) */
    .priv-drawer { top: 0; bottom: 0; height: 100vh; height: 100dvh; border-radius: 0; z-index: 20; }
    .priv-drawer .sheet-handle { display: none; }
    .priv-drawer .live-head { position: sticky; top: 0; background: var(--surface-02); z-index: 1; }
  }
  @media (max-width: 599px) and (prefers-reduced-motion: reduce) {
    .live-drawer { transition: none !important; }
  }

  /* ===================== touch / pointer ==================== */
  @media (hover: hover) { .ev:hover .ev-del { color: var(--text-secondary); } }
  @media (hover: none)  { .ev-del { color: var(--text-secondary); } }  /* never hover-only */
  @media (pointer: coarse) {
    .btn-text, .digest-chip, .send, .menu-item, .m-text-btn, .priv-excl-add button { min-height: 44px; }
    .live-close, .btn-icon { min-width: 44px; min-height: 44px; }
    .ev-del, .excl-chip button { min-width: 44px; min-height: 44px; justify-content: center; }
    /* keep chip visuals small; expand only the tap area via a centered pseudo-element */
    .chip, .scope-chip, .excl-chip { position: relative; }
    .chip::before, .scope-chip::before, .excl-chip::before {
      content: ''; position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); height: 44px; }
    /* switch: grow the invisible input hit area without moving the visible track */
    .switch input { top: -12px; left: -6px; width: 48px; height: 44px; }
  }

  /* -- OCR capture snackbar (Material snackbar, bottom-center) -------------- */
  .snack { position: fixed; bottom: 140px; left: 50%; transform: translateX(-50%) translateY(16px);
    background: var(--surface-12); color: var(--text-primary); border-radius: var(--radius);
    box-shadow: var(--elevation-8); padding: 10px 16px; font: 400 13px/1.4 var(--font);
    max-width: min(480px, 90vw); display: flex; align-items: center; gap: 10px;
    opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s;
    z-index: 50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .snack.show { opacity: 1; transform: translateX(-50%) translateY(0); pointer-events: auto; }
  .snack .sk { flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--k-ocr); }
</style>
</head>
<body>
<header>
  <div class="logo">Hind<span>sight</span></div>
  <div class="tag">your PC's memory · stays on your PC</div>
  <div class="hstats" id="hstats"><span id="hcount">0</span><span class="hword">&nbsp;memories</span><span class="hword-full">&nbsp;remembered</span></div>
  <button class="btn-text ripple-host state-layer appbar-action" id="livetoggle" tabindex="7"
    aria-label="Toggle live capture feed" title="Watch memories form in real time" style="color:var(--primary)">
    <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49"/><path d="M7.76 16.24a6 6 0 0 1 0-8.49"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M4.93 19.07a10 10 0 0 1 0-14.14"/></svg>
    Live
  </button>
  <button class="btn-text ripple-host state-layer appbar-action" id="privacybtn" tabindex="8"
    aria-label="Privacy controls" title="Pause capture, choose sources, exclude sites" style="color:var(--text-secondary)">
    <svg class="ic" id="privacyicon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    <span id="privacylabel">Privacy</span>
  </button>
  <button class="btn-text ripple-host state-layer appbar-action" id="forget" tabindex="9"
    aria-label="Forget all" title="Permanently delete every stored memory">
    <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
    Forget all
  </button>
  <button class="btn-icon ripple-host state-layer appbar-more" id="overflowbtn"
    aria-label="More actions" aria-haspopup="menu" aria-expanded="false" title="More">
    <svg class="ic" viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>
  </button>
  <div class="menu" id="overflowmenu" role="menu" aria-hidden="true">
    <button class="menu-item ripple-host state-layer" role="menuitem" data-act="live">
      <svg class="ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49"/><path d="M7.76 16.24a6 6 0 0 1 0-8.49"/></svg>
      Live capture
    </button>
    <button class="menu-item ripple-host state-layer" role="menuitem" data-act="privacy">
      <svg class="ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      <span id="menuprivacylabel">Privacy</span>
    </button>
    <button class="menu-item menu-item-error ripple-host state-layer" role="menuitem" data-act="forget">
      <svg class="ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
      Forget all
    </button>
  </div>
  <div class="chip-status" id="badge">
    <span class="status-dot" id="dot"></span>
    <svg class="ic" id="badgeicon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="display:none"><path d="M2 8.82a15 15 0 0 1 4.17-2.65"/><path d="M10.66 5.07a15 15 0 0 1 11.34 3.75"/><path d="M16.85 11.4a10 10 0 0 1 2.5 1.65"/><path d="M5 12.55a10 10 0 0 1 2.5-1.65"/><path d="M8.5 16.15a5 5 0 0 1 7 0"/><line x1="12" y1="20" x2="12.01" y2="20"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
    <span id="badgetext">checking…</span>
  </div>
</header>
<main>
  <div class="hero" id="hero">
    <h1>Ask your past.</h1>
    <p>Everything you've seen, copied, and read — searchable, and 100% local.</p>
    <div class="chips" id="chips">
      <div class="chip ripple-host state-layer" tabindex="1">What was I working on this morning?</div>
      <div class="chip ripple-host state-layer" tabindex="2">What articles did I read about embeddings?</div>
      <div class="chip ripple-host state-layer" tabindex="3">What did I copy to my clipboard earlier?</div>
      <div class="chip ripple-host state-layer" tabindex="4">Which GitHub repos did I look at today?</div>
    </div>
    <div class="digest-row">
      <button class="digest-chip ripple-host state-layer" id="digestbtn">
        <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        Summarize my day
      </button>
    </div>
  </div>
  <div class="thread" id="thread" aria-live="polite"></div>
</main>
<div class="sheet-scrim" id="sheetscrim"></div>
<aside class="live-drawer" id="livedrawer" aria-label="Live capture feed" aria-hidden="true">
  <div class="sheet-handle" aria-hidden="true"></div>
  <div class="live-head">
    <span class="rec" id="liverec"></span>
    <div>
      <div class="live-title">Live capture</div>
      <div class="live-sub" id="livesub">watching for new memories…</div>
    </div>
    <button class="live-close" id="liveclose" aria-label="Close live feed">
      <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
  </div>
  <div class="live-list" id="livelist" aria-live="polite"></div>
</aside>
<aside class="live-drawer priv-drawer" id="privacydrawer" aria-label="Privacy controls" aria-hidden="true">
  <div class="sheet-handle" aria-hidden="true"></div>
  <div class="live-head">
    <svg class="ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="color:var(--primary)"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    <div class="grow">
      <div class="live-title">Privacy</div>
      <div class="live-sub">your memory, your rules</div>
    </div>
    <button class="live-close" id="privclose" aria-label="Close privacy panel">
      <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
  </div>
  <div class="priv-body">
    <div class="priv-pause">
      <div class="grow">
        <div class="priv-status" id="privstatus">Recording</div>
        <div class="live-sub" id="privstatussub">capturing new activity</div>
      </div>
      <label class="switch"><input type="checkbox" id="recsw" checked aria-label="Recording"><span class="track"></span><span class="thumb"></span></label>
    </div>
    <div class="priv-section-title">Capture sources</div>
    <div class="priv-row"><div class="grow">Browser history<div class="sub">pages you visit</div></div><label class="switch"><input type="checkbox" data-src="browser" aria-label="Capture browser history"><span class="track"></span><span class="thumb"></span></label></div>
    <div class="priv-row"><div class="grow">Window titles<div class="sub">apps and files in focus</div></div><label class="switch"><input type="checkbox" data-src="window" aria-label="Capture window titles"><span class="track"></span><span class="thumb"></span></label></div>
    <div class="priv-row"><div class="grow">Clipboard<div class="sub">text you copy</div></div><label class="switch"><input type="checkbox" data-src="clipboard" aria-label="Capture clipboard"><span class="track"></span><span class="thumb"></span></label></div>
    <div class="priv-row"><div class="grow">Screen OCR<div class="sub">reads on-screen text (on by default)</div></div><label class="switch"><input type="checkbox" data-src="ocr" aria-label="Capture screen OCR"><span class="track"></span><span class="thumb"></span></label></div>
    <div class="priv-divider"></div>
    <div class="priv-section-title">Never capture</div>
    <div class="priv-excl-add">
      <input id="exclinput" type="text" placeholder="domain or app name…" aria-label="Add an exclusion" autocomplete="off" />
      <button class="ripple-host" id="excladd">Add</button>
    </div>
    <div id="excllist"></div>
  </div>
</aside>
<div class="composer">
  <div class="box scopes" id="scopes" role="group" aria-label="Time scope">
    <button class="scope-chip ripple-host active" data-scope="all">All time</button>
    <button class="scope-chip ripple-host" data-scope="today">Today</button>
    <button class="scope-chip ripple-host" data-scope="yesterday">Yesterday</button>
    <button class="scope-chip ripple-host" data-scope="week">This week</button>
  </div>
  <div class="box">
    <div class="field">
      <input id="q" type="text" placeholder=" " autocomplete="off" tabindex="5" />
      <label for="q">Ask about anything you've done on this machine…</label>
    </div>
    <button class="send ripple-host state-layer" id="send" tabindex="6" aria-label="Recall">
      <svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      <span class="send-label">Recall</span>
    </button>
  </div>
</div>
<div id="snack" class="snack" role="status" aria-live="polite"><span class="sk"></span><span id="snackmsg"></span></div>
<script>
const $ = s => document.querySelector(s);
const thread = $('#thread'), input = $('#q'), send = $('#send'), header = $('header');

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
    el.addEventListener('pointerdown', e => ripple(el, e));
  });
}
wireRipples(document);

// App bar: flush at rest, elevates once content has scrolled under it.
addEventListener('scroll', () => { header.classList.toggle('raised', scrollY > 4); });

async function health() {
  try {
    const r = await fetch('/api/health'); const j = await r.json();
    $('#dot').classList.toggle('off', !j.ok);
    $('#badgeicon').style.display = j.ok ? 'none' : 'inline-block';
    $('#badgetext').textContent = j.ok ? 'Local · Offline-capable' : 'Supermemory Local not reachable';
  } catch {
    $('#dot').classList.add('off'); $('#badgeicon').style.display = 'inline-block';
    $('#badgetext').textContent = 'offline';
  }
}
health(); setInterval(health, 8000);

async function refreshStats(){
  try { const r = await fetch('/api/stats'); const j = await r.json();
    $('#hcount').textContent = (j.memoryCount || 0);
  } catch {}
}
refreshStats(); setInterval(refreshStats, 8000);

// -- app-bar overflow menu (phone) ----------------------------------------
const overflowBtn = $('#overflowbtn'), overflowMenu = $('#overflowmenu');
function closeMenu(){ overflowMenu.classList.remove('open'); overflowMenu.setAttribute('aria-hidden','true'); overflowBtn.setAttribute('aria-expanded','false'); }
function openMenu(){ overflowMenu.classList.add('open'); overflowMenu.setAttribute('aria-hidden','false'); overflowBtn.setAttribute('aria-expanded','true'); }
overflowBtn.addEventListener('click', (e) => { e.stopPropagation(); overflowMenu.classList.contains('open') ? closeMenu() : openMenu(); });
document.addEventListener('click', (e) => { if (!overflowMenu.contains(e.target) && e.target !== overflowBtn) closeMenu(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
overflowMenu.addEventListener('click', (e) => {
  const item = e.target.closest('[data-act]'); if (!item) return;
  closeMenu();
  const act = item.dataset.act;
  if (act === 'live') openLive();
  else if (act === 'privacy') openPrivacy();
  else if (act === 'forget') forgetAll();
});

function esc(s){ return (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

const KIND_LABEL = { clipboard:'Clipboard', window:'Window', browser:'Browser', ocr:'OCR' };
function relTime(iso){
  const t = new Date(iso).getTime(); if (isNaN(t)) return '';
  const s = Math.max(0, (Date.now()-t)/1000);
  if (s < 60)    return Math.floor(s) + 's ago';
  if (s < 3600)  return Math.floor(s/60) + 'm ago';
  if (s < 86400) return Math.floor(s/3600) + 'h ago';
  return Math.floor(s/86400) + 'd ago';
}

// -- OCR snackbar toast -------------------------------------------------------
const snack = $('#snack'), snackMsg = $('#snackmsg');
let snackTimer = null;
function showSnack(text) {
  snackMsg.textContent = text;
  snack.classList.add('show');
  clearTimeout(snackTimer);
  snackTimer = setTimeout(() => snack.classList.remove('show'), 3500);
}

// -- live capture feed: poll newest memories while the drawer is open -----
const liveDrawer = $('#livedrawer'), liveList = $('#livelist');
let liveOpen = false, liveTimer = null, seenIds = new Set(), livePrimed = false, lastSig = '';

// Background OCR-toast poll: runs always, shows snack when the drawer is closed
let bgSeenIds = new Set(), bgPrimed = false;
async function pollBg(){
  try {
    const r = await fetch('/api/recent?limit=6'); const j = await r.json();
    const ms = j.memories || [];
    if (bgPrimed && !liveOpen) {
      const newOcr = ms.filter(m => m.kind === 'ocr' && !bgSeenIds.has(m.id));
      if (newOcr.length) {
        const preview = newOcr[0].content.slice(0, 60) + (newOcr[0].content.length > 60 ? '…' : '');
        showSnack('Screen captured · ' + preview);
      }
    }
    ms.forEach(m => bgSeenIds.add(m.id));
    bgPrimed = true;
  } catch {}
}
setInterval(pollBg, 8000);
pollBg();

async function pollRecent(){
  try {
    const r = await fetch('/api/recent?limit=12'); const j = await r.json();
    const ms = j.memories || [];
    const sig = ms.map(m => m.id).join(',');
    if (sig !== lastSig) {
      liveList.innerHTML = ms.length ? ms.map(m => {
        const isNew = livePrimed && !seenIds.has(m.id);
        const k = m.kind || 'window';
        return `<div class="live-item${isNew ? ' fresh' : ''}">
          <div class="lc">${esc(m.content)}</div>
          <div class="lm"><span class="kdot k-${esc(k)}"></span><span class="kind-label">${esc(KIND_LABEL[k]||k)}</span> · ${esc(relTime(m.captured_at))}</div>
        </div>`;
      }).join('') : '<div class="live-empty">No memories yet — start the capture daemon, or copy some text and watch it appear.</div>';
      lastSig = sig;
    }
    ms.forEach(m => seenIds.add(m.id));
    livePrimed = true;
    $('#livesub').textContent = ms.length ? (ms.length + ' most recent') : 'watching for new memories…';
  } catch {}
}
const sheetScrim = $('#sheetscrim');
function openLive(){
  closePrivacy();
  liveOpen = true; liveDrawer.classList.add('open'); liveDrawer.setAttribute('aria-hidden','false');
  sheetScrim.classList.add('show');   // dims content behind the bottom sheet (phone only, via CSS)
  seenIds = new Set(); livePrimed = false; lastSig = '';
  pollRecent(); liveTimer = setInterval(pollRecent, 4000);
}
function closeLive(){
  liveOpen = false; liveDrawer.classList.remove('open'); liveDrawer.setAttribute('aria-hidden','true');
  sheetScrim.classList.remove('show');
  clearInterval(liveTimer); liveTimer = null;
}
$('#livetoggle').addEventListener('click', () => liveOpen ? closeLive() : openLive());
$('#liveclose').addEventListener('click', closeLive);
sheetScrim.addEventListener('click', closeLive);           // tap scrim to dismiss the sheet
liveDrawer.querySelector('.sheet-handle').addEventListener('click', closeLive);  // tap handle to dismiss

// -- privacy control center ------------------------------------------------
const privDrawer = $('#privacydrawer');
let settings = { paused:false, sources:{}, exclusions:[] };
const X_SVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
function applyPrivacyBtn(){
  $('#privacylabel').textContent = settings.paused ? 'Paused' : 'Privacy';
  $('#privacybtn').style.color = settings.paused ? 'var(--error)' : 'var(--text-secondary)';
  const ml = $('#menuprivacylabel'); if (ml) ml.textContent = settings.paused ? 'Privacy · Paused' : 'Privacy';
}
function renderPrivacy(){
  $('#recsw').checked = !settings.paused;
  const st = $('#privstatus');
  st.textContent = settings.paused ? 'Paused' : 'Recording';
  st.classList.toggle('paused', settings.paused);
  $('#privstatussub').textContent = settings.paused ? 'not capturing new activity' : 'capturing new activity';
  document.querySelectorAll('[data-src]').forEach(sw => { sw.checked = settings.sources[sw.dataset.src] !== false; });
  const list = $('#excllist');
  list.innerHTML = (settings.exclusions && settings.exclusions.length)
    ? settings.exclusions.map(x => `<span class="excl-chip">${esc(x)}<button data-x="${esc(x)}" aria-label="Remove ${esc(x)}">${X_SVG}</button></span>`).join('')
    : '<div class="priv-empty">Nothing excluded yet. Add a domain (chase.com) or app name to never capture it.</div>';
  applyPrivacyBtn();
}
async function loadSettings(){
  try { const r = await fetch('/api/settings'); settings = await r.json(); } catch {}
  renderPrivacy();
}
async function saveSettings(patch){
  try {
    const r = await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(patch)});
    settings = await r.json();
  } catch {}
  renderPrivacy();
}
$('#recsw').addEventListener('change', e => saveSettings({ paused: !e.target.checked }));
document.querySelectorAll('[data-src]').forEach(sw =>
  sw.addEventListener('change', () => saveSettings({ sources: { [sw.dataset.src]: sw.checked } })));
$('#excladd').addEventListener('click', () => {
  const v = $('#exclinput').value.trim(); if (!v) return;
  const cur = settings.exclusions || [];
  if (!cur.includes(v)) saveSettings({ exclusions: cur.concat([v]) });
  $('#exclinput').value = '';
});
$('#exclinput').addEventListener('keydown', e => { if (e.key==='Enter'){ e.preventDefault(); $('#excladd').click(); } });
$('#excllist').addEventListener('click', e => {
  const b = e.target.closest('[data-x]'); if (!b) return;
  saveSettings({ exclusions: (settings.exclusions||[]).filter(x => x !== b.dataset.x) });
});
function openPrivacy(){ closeLive(); privDrawer.classList.add('open'); privDrawer.setAttribute('aria-hidden','false'); loadSettings(); }
function closePrivacy(){ privDrawer.classList.remove('open'); privDrawer.setAttribute('aria-hidden','true'); }
$('#privacybtn').addEventListener('click', () => privDrawer.classList.contains('open') ? closePrivacy() : openPrivacy());
$('#privclose').addEventListener('click', closePrivacy);
loadSettings();   // reflect paused state in the app bar from load

// Material Dialog — replaces native confirm() for "Forget all". The gate
// (destructive call only fires if the user picks the confirm action) is
// identical to a plain confirm(); the chrome is a real, focus-trapped
// Material dialog that defaults focus to the safe (Cancel) action.
function materialConfirm(title, message, confirmLabel, cancelLabel){
  return new Promise(resolve => {
    const scrim = document.createElement('div'); scrim.className = 'm-scrim';
    scrim.innerHTML = `<div class="m-dialog" role="alertdialog" aria-modal="true" aria-labelledby="mdt" aria-describedby="mdb">
      <div class="m-dialog-title" id="mdt">${esc(title)}</div>
      <div class="m-dialog-body" id="mdb">${esc(message)}</div>
      <div class="m-dialog-actions">
        <button class="m-text-btn ripple-host" data-a="cancel">${esc(cancelLabel)}</button>
        <button class="m-text-btn m-text-btn-error ripple-host" data-a="confirm">${esc(confirmLabel)}</button>
      </div></div>`;
    document.body.appendChild(scrim);
    wireRipples(scrim);

    const cancelBtn = scrim.querySelector('[data-a="cancel"]');
    const confirmBtn = scrim.querySelector('[data-a="confirm"]');
    const focusables = [cancelBtn, confirmBtn];
    cancelBtn.focus();   // safe default for a destructive action

    function trapTab(e){
      if (e.key !== 'Tab') return;
      e.preventDefault();
      const i = focusables.indexOf(document.activeElement);
      const next = e.shiftKey
        ? focusables[(i <= 0 ? focusables.length : i) - 1]
        : focusables[(i + 1) % focusables.length];
      next.focus();
    }
    function onKey(e){ if (e.key === 'Escape') close(false); }
    function close(result){
      scrim.remove();
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('keydown', trapTab);
      resolve(result);
    }
    document.addEventListener('keydown', onKey);
    document.addEventListener('keydown', trapTab);
    scrim.addEventListener('click', e => {
      if (e.target === scrim) return close(false);
      const a = e.target.closest('[data-a]');
      if (!a) return;
      close(a.dataset.a === 'confirm');
    });
  });
}

async function forgetAll(){
  const ok = await materialConfirm(
    'Forget everything?',
    'This permanently deletes every stored memory. This cannot be undone.',
    'Delete', 'Cancel'
  );
  if (!ok) return;
  await fetch('/api/forget_all', {method:'POST'});
  thread.innerHTML=''; $('#hero').style.display='';
  refreshStats();
}
$('#forget').addEventListener('click', forgetAll);

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
function renderEvidence(ev, note){
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
    // Relevance bar only when there's a real relevance score (search results);
    // chronological evidence (the digest) has no score, so we omit it.
    const relev = (e.score||0) > 0
      ? `<div class="relev" title="relevance ${pct}%"><div class="bar"><span style="width:${pct}%"></span></div>${pct}%</div>`
      : '';
    const del = e.id ? `<button class="ev-del" data-del="${esc(e.id)}" aria-label="Forget this memory" title="Forget this memory"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg></button>` : '';
    return `<div class="ev ripple-host state-layer" tabindex="0" data-id="${esc(e.id||'')}"><div class="body">
      <div class="content">${esc(e.content)}</div>
      <div class="meta"><span class="kdot k-${esc(k)}"></span><span class="kind-label">${esc(label)}</span> · ${when}${src? ' · '+src : ''}</div></div>
      ${relev}${del}</div>`;
  }).join('');
  const word = note === undefined ? 'matching ' : (note ? note + ' ' : '');
  return `<div class="evidence"><h4>Evidence · ${shown.length} ${word}${shown.length===1?'memory':'memories'}</h4>${rows}</div>`;
}

async function ask(text){
  addUser(text); $('#hero').style.display='none';
  const bubble = addAI().querySelector('.bubble');
  send.disabled = true;
  try {
    const r = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({question: text, scope: activeScope})});
    const j = await r.json();
    if(j.error){ bubble.innerHTML = 'Error: ' + esc(j.error); }
    else {
      const scopeName = {today:'Today', yesterday:'Yesterday', week:'This week'}[j.scope];
      const scopeTag = scopeName ? `<div class="scope-tag"><span class="kdot"></span>Scope · ${scopeName}</div>` : '';
      bubble.innerHTML = esc(j.answer) + scopeTag
        + `<div class="engine">answered by ${esc(j.engine)}</div>`
        + renderEvidence(j.evidence);
      wireRipples(bubble);
    }
  } catch(e){ bubble.textContent = 'Request failed: ' + e; }
  send.disabled = false; scroll();
}
async function runDigest(){
  addUser('Summarize my day'); $('#hero').style.display='none';
  const bubble = addAI().querySelector('.bubble');
  send.disabled = true;
  try {
    const r = await fetch('/api/digest', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})});
    const j = await r.json();
    const dateTag = j.date ? `<div class="scope-tag"><span class="kdot"></span>Digest · ${esc(j.date)}</div>` : '';
    bubble.innerHTML = esc(j.answer) + dateTag
      + `<div class="engine">answered by ${esc(j.engine)}</div>`
      + renderEvidence(j.evidence, '');
    wireRipples(bubble);
  } catch(e){ bubble.textContent = 'Request failed: ' + e; }
  send.disabled = false; scroll();
}
$('#digestbtn').addEventListener('click', runDigest);

// Per-memory forget: delete icon on any evidence row (delegated).
thread.addEventListener('click', async (e) => {
  const b = e.target.closest('.ev-del'); if (!b) return;
  e.stopPropagation();
  const ok = await materialConfirm('Forget this memory?',
    'This permanently deletes this single memory from your history.', 'Delete', 'Cancel');
  if (!ok) return;
  try { await fetch('/api/forget_one', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id: b.dataset.del})}); } catch {}
  const row = b.closest('.ev'); if (row) row.remove();
  refreshStats();
});

function scroll(){ window.scrollTo(0, document.body.scrollHeight); }
function go(){ const t = input.value.trim(); if(!t) return; input.value=''; ask(t); }
send.addEventListener('click', () => go());
input.addEventListener('keydown', e => { if(e.key==='Enter') go(); });
document.querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => ask(c.textContent)));

let activeScope = 'all';
document.querySelectorAll('.scope-chip').forEach(c => c.addEventListener('click', () => {
  document.querySelectorAll('.scope-chip').forEach(x => x.classList.remove('active'));
  c.classList.add('active'); activeScope = c.dataset.scope;
}));
</script>
</body>
</html>
"""
