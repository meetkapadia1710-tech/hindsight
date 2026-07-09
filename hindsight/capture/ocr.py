"""Optional screenshot OCR using the Windows built-in OCR engine.

Captures the foreground window region and runs Windows.Media.Ocr (via the
`winsdk`/`winrt` package) entirely on-device — no cloud OCR. Text is what
gets stored; the screenshot itself is never persisted unless you ask.

This is a stretch feature: it is only imported if enabled, so the core
daemon has no dependency on winsdk.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class OcrResult:
    text: str


def available() -> bool:
    try:
        import winsdk  # noqa: F401
        from PIL import ImageGrab  # noqa: F401
        return True
    except ImportError:
        return False


async def _ocr_bytes(png_bytes: bytes) -> str:
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.storage.streams import (
        DataWriter, InMemoryRandomAccessStream,
    )

    stream = InMemoryRandomAccessStream()
    writer = DataWriter(stream.get_output_stream_at(0))
    writer.write_bytes(list(png_bytes))
    await writer.store_async()
    stream.seek(0)

    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()

    engine = OcrEngine.try_create_from_language(Language("en-US"))
    if engine is None:
        engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        return ""
    result = await engine.recognize_async(bitmap)
    return result.text or ""


def ocr_foreground() -> OcrResult | None:
    """Grab the whole screen and OCR it. Returns None if unavailable."""
    if not available():
        return None
    import io
    from PIL import ImageGrab

    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    text = asyncio.run(_ocr_bytes(buf.getvalue()))
    text = " ".join(text.split())
    if len(text) < 12:
        return None
    return OcrResult(text=text[:1500])
