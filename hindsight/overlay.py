"""Hindsight system-tray + global hotkey overlay.

Win+H → compact floating search window appears over whatever you're doing.
Type a question, press Enter → answer from local memory in ~2s.
Escape or click X → dismiss.

Run with:  python -m hindsight.overlay
Requires:  pystray  keyboard  (pip install pystray keyboard)
Pillow is already a dependency for OCR.
"""

from __future__ import annotations

import json
import sys
import threading
import tkinter as tk
import urllib.request
from tkinter import ttk

APP_URL = "http://127.0.0.1:8787"
_overlay_win: "OverlayWindow | None" = None
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# HTTP helper (stdlib only)
# ---------------------------------------------------------------------------

def _ask(question: str) -> dict:
    payload = json.dumps({"question": question, "limit": 5}).encode()
    req = urllib.request.Request(
        f"{APP_URL}/api/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as exc:
        return {"answer": f"Error: {exc}", "engine": "error", "evidence": []}


# ---------------------------------------------------------------------------
# Tray icon image (16×16 solid square with "H")
# ---------------------------------------------------------------------------

def _make_icon():
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (64, 64), (144, 202, 249, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 6), "H", fill=(18, 18, 18, 255), font=font)
    return img


# ---------------------------------------------------------------------------
# Overlay window
# ---------------------------------------------------------------------------

class OverlayWindow:
    BG = "#1e1e1e"
    FG = "#ffffffde"
    FG2 = "#ffffff99"
    ACC = "#90caf9"
    FONT = ("Segoe UI", 13)
    FONT_SMALL = ("Segoe UI", 11)

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Hindsight")
        self.root.configure(bg=self.BG)
        self.root.overrideredirect(True)          # no title bar
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self._build_ui()
        self._center()
        self.root.bind("<Escape>", lambda _: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.focus_force()

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=self.ACC, padx=2, pady=2)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg=self.BG, padx=20, pady=16)
        inner.pack(fill="both", expand=True)

        # Header row
        hdr = tk.Frame(inner, bg=self.BG)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="Hind", font=("Segoe UI", 15, "bold"),
                 bg=self.BG, fg=self.FG).pack(side="left")
        tk.Label(hdr, text="sight", font=("Segoe UI", 15, "bold"),
                 bg=self.BG, fg=self.ACC).pack(side="left")
        tk.Label(hdr, text="  Win+H  ·  Esc to close",
                 font=self.FONT_SMALL, bg=self.BG, fg=self.FG2).pack(side="left", padx=8)
        close_btn = tk.Label(hdr, text="✕", font=self.FONT, bg=self.BG, fg=self.FG2,
                             cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.close())

        # Query input
        self.entry = tk.Entry(inner, font=("Segoe UI", 14), bg="#2c2c2c", fg=self.FG,
                              insertbackground=self.ACC, relief="flat",
                              highlightthickness=1, highlightbackground=self.ACC,
                              highlightcolor=self.ACC)
        self.entry.pack(fill="x", ipady=8)
        self.entry.bind("<Return>", self._on_submit)
        self.entry.focus_set()

        # Status / answer area
        self.status = tk.Label(inner, text="Type a question and press Enter",
                               font=self.FONT_SMALL, bg=self.BG, fg=self.FG2,
                               wraplength=560, justify="left", anchor="w")
        self.status.pack(fill="x", pady=(10, 0))

        self.answer_frame = tk.Frame(inner, bg=self.BG)
        self.answer_frame.pack(fill="both", expand=True, pady=(8, 0))

        # Colored left-border strip — color set in _show() based on evidence kind
        self.answer_strip = tk.Frame(self.answer_frame, bg=self.ACC, width=3)
        self.answer_strip.pack(side="left", fill="y")
        self.answer_strip.pack_propagate(False)

        self.answer_text = tk.Text(
            self.answer_frame, font=self.FONT, bg="#242424", fg=self.FG,
            relief="flat", wrap="word", state="disabled",
            height=6, padx=10, pady=10,
            highlightthickness=0,
        )
        self.answer_text.pack(fill="both", expand=True)

        # Evidence chips row
        self.ev_frame = tk.Frame(inner, bg=self.BG)
        self.ev_frame.pack(fill="x", pady=(8, 0))

    def _center(self) -> None:
        w, h = 600, 360
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = int(sh * 0.28)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(w, h)

    def _on_submit(self, _=None) -> None:
        q = self.entry.get().strip()
        if not q:
            return
        self._set_status("Searching your memory…")
        self._clear_answer()
        threading.Thread(target=self._fetch, args=(q,), daemon=True).start()

    def _fetch(self, q: str) -> None:
        result = _ask(q)
        self.root.after(0, self._show, result)

    def _show(self, result: dict) -> None:
        answer = result.get("answer") or "(no answer)"
        engine = result.get("engine") or ""
        evidence = result.get("evidence") or []

        # Color left border by top evidence kind (pink for OCR, blue for default)
        top_kind = (evidence[0].get("kind") or "") if evidence else ""
        border_color = "#f06292" if top_kind == "ocr" else "#90caf9"
        self.answer_strip.configure(bg=border_color)

        self._set_status(f"answered by {engine}")
        self._set_answer(answer)

        # Clear old evidence chips
        for w in self.ev_frame.winfo_children():
            w.destroy()

        for ev in evidence[:5]:
            content = (ev.get("content") or "")[:60]
            kind = ev.get("kind") or "window"
            color = {"clipboard": "#ffb74d", "browser": "#66bb6a",
                     "ocr": "#f06292"}.get(kind, "#90caf9")
            chip = tk.Frame(self.ev_frame, bg="#2c2c2c", padx=6, pady=3)
            chip.pack(side="left", padx=(0, 6), pady=2)
            dot = tk.Frame(chip, bg=color, width=6, height=6)
            dot.pack(side="left", padx=(0, 4))
            tk.Label(chip, text=content, font=("Segoe UI", 10),
                     bg="#2c2c2c", fg=self.FG2).pack(side="left")

    def _set_status(self, msg: str) -> None:
        self.status.configure(text=msg)

    def _clear_answer(self) -> None:
        self.answer_strip.configure(bg=self.ACC)
        self.answer_text.configure(state="normal")
        self.answer_text.delete("1.0", "end")
        self.answer_text.configure(state="disabled")
        for w in self.ev_frame.winfo_children():
            w.destroy()

    def _set_answer(self, text: str) -> None:
        self.answer_text.configure(state="normal")
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", text)
        self.answer_text.configure(state="disabled")

    def close(self) -> None:
        global _overlay_win
        with _lock:
            _overlay_win = None
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Hotkey + tray
# ---------------------------------------------------------------------------

def _open_overlay() -> None:
    global _overlay_win
    with _lock:
        if _overlay_win is not None:
            try:
                _overlay_win.root.lift()
                _overlay_win.root.focus_force()
            except Exception:
                _overlay_win = None
            else:
                return
        win = OverlayWindow()
        _overlay_win = win
    win.run()


def _hotkey_callback() -> None:
    threading.Thread(target=_open_overlay, daemon=True).start()


def main() -> None:
    import keyboard
    import pystray

    try:
        icon_img = _make_icon()
    except Exception:
        from PIL import Image
        icon_img = Image.new("RGBA", (64, 64), (144, 202, 249, 255))

    def open_app(_=None):
        import webbrowser
        webbrowser.open(APP_URL)

    def quit_app(icon, _=None):
        keyboard.unhook_all_hotkeys()
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Open Hindsight", open_app, default=True),
        pystray.MenuItem("Quick search  Win+H", _hotkey_callback),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )
    icon = pystray.Icon("Hindsight", icon_img, "Hindsight", menu)

    keyboard.add_hotkey("windows+h", _hotkey_callback, suppress=True)
    print("[hindsight] tray icon running. Win+H to search. Right-click tray icon to quit.")
    icon.run()


if __name__ == "__main__":
    main()
