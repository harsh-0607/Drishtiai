from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Optional, Tuple


class WhisperService:
    """Speech-to-text using faster-whisper.

    Note: This requires FFmpeg in many environments.
    """

    def __init__(self, model: str = "base") -> None:
        self._model_name = model
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8")
        return self._model

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> Tuple[str, Optional[str]]:
        def _sync() -> Tuple[str, Optional[str]]:
            model = self._load()
            # Write to temp file because faster-whisper expects a path.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                f.write(audio_bytes)
                tmp_path = f.name

            try:
                segments, info = model.transcribe(tmp_path, language=language)
                text = "".join(seg.text for seg in segments).strip()
                detected = getattr(info, "language", None)
                return text, detected
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        return await asyncio.to_thread(_sync)
