from __future__ import annotations

import asyncio
import io
import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service using EasyOCR with pytesseract fallback."""

    def __init__(self) -> None:
        self._easyocr_reader = None

    def _easyocr_langs(self, lang: str) -> list[str]:
        # EasyOCR language codes differ. Keep minimal mapping.
        mapping = {
            "en": ["en"],
            "hi": ["hi", "en"],
            "ta": ["ta", "en"],
            "te": ["te", "en"],
            "bn": ["bn", "en"],
            "mr": ["mr", "en"],
            "gu": ["gu", "en"],
            "kn": ["kn", "en"],
            "ml": ["ml", "en"],
            "pa": ["en"],
        }
        return mapping.get(lang, ["hi", "en"])

    def _get_reader(self, lang: str):
        if self._easyocr_reader is None:
            import easyocr

            self._easyocr_reader = easyocr.Reader(
                self._easyocr_langs(lang),
                gpu=False,
            )
        return self._easyocr_reader

    async def read_text(self, image_bytes: bytes, language: str) -> Tuple[str, Optional[float]]:
        """Extract text from image.

        Returns (text, avg_confidence)
        """

        def _sync_read() -> Tuple[str, Optional[float]]:
            # Decode bytes into PIL
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            np_img = np.array(img)

            # EasyOCR
            try:
                reader = self._get_reader(language)
                results = reader.readtext(np_img)
                if results:
                    texts = [r[1] for r in results if r and len(r) > 1]
                    confs = [float(r[2]) for r in results if r and len(r) > 2]
                    text = " ".join(t.strip() for t in texts if t.strip()).strip()
                    avg_conf = (sum(confs) / len(confs)) if confs else None
                    if text:
                        return text, avg_conf
            except Exception:
                logger.exception("EasyOCR failed; falling back to pytesseract")

            # pytesseract fallback
            try:
                import pytesseract

                text = pytesseract.image_to_string(img)
                text = (text or "").strip()
                return text, None
            except Exception:
                logger.exception("pytesseract failed")
                return "", None

        return await asyncio.to_thread(_sync_read)
