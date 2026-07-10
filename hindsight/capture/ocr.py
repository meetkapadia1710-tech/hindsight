"""Optional screenshot OCR using the Windows built-in OCR engine.

Grabs the screen and runs Windows.Media.Ocr (via the `winrt` packages)
entirely on-device — no cloud OCR. The recognized text is what gets stored;
the screenshot itself is never persisted.

This is an opt-in feature (config `[capture] ocr = true`) and is imported
lazily, so the core daemon has no dependency on winrt/Pillow.
"""

from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass


@dataclass
class OcrResult:
    text: str


def available() -> bool:
    try:
        import winrt.windows.media.ocr  # noqa: F401
        from PIL import ImageGrab  # noqa: F401
        return True
    except Exception:
        return False


async def _ocr_software_bitmap(png_bytes: bytes) -> str:
    from winrt.windows.storage.streams import (
        DataWriter, InMemoryRandomAccessStream,
    )
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language

    stream = InMemoryRandomAccessStream()
    writer = DataWriter(stream.get_output_stream_at(0))
    writer.write_bytes(png_bytes)
    await writer.store_async()
    await writer.flush_async()
    stream.seek(0)

    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()

    engine = None
    try:
        engine = OcrEngine.try_create_from_language(Language("en-US"))
    except Exception:
        engine = None
    if engine is None:
        engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        return ""
    result = await engine.recognize_async(bitmap)
    return result.text or ""


def ocr_image(img) -> str:
    """OCR a PIL image, returning recognized text (may be empty)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return asyncio.run(_ocr_software_bitmap(buf.getvalue()))


def ocr_screen(min_chars: int = 16, max_chars: int = 1500) -> OcrResult | None:
    """Grab the screen and OCR it. Returns None if unavailable or too little
    text was found (avoids storing noise)."""
    if not available():
        return None
    from PIL import ImageGrab

    text = " ".join(ocr_image(ImageGrab.grab()).split())
    if len(text) < min_chars:
        return None
    return OcrResult(text=text[:max_chars])
