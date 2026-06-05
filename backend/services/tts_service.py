from __future__ import annotations

import asyncio
import base64
import io
from typing import Optional, Tuple

import edge_tts


class TTSService:
    """Text-to-speech service using edge-tts (fast, good voices).

    Returns MP3 bytes.
    """

    def _voice_for_language(self, language: str) -> str:
        # Simple mapping; you can expand later.
        mapping = {
            "hi": "hi-IN-SwaraNeural",
            "en": "en-IN-NeerjaNeural",
            "ta": "ta-IN-PallaviNeural",
            "te": "te-IN-ShrutiNeural",
            "bn": "bn-IN-TanishaaNeural",
            "mr": "mr-IN-AarohiNeural",
            "gu": "gu-IN-DhwaniNeural",
            "kn": "kn-IN-SapnaNeural",
            "ml": "ml-IN-SobhanaNeural",
            "pa": "pa-IN-VaaniNeural",
        }
        return mapping.get(language, "hi-IN-SwaraNeural")

    async def synthesize(self, text: str, language: str) -> bytes:
        voice = self._voice_for_language(language)
        communicate = edge_tts.Communicate(text=text, voice=voice)
        out = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                out.extend(chunk["data"])
        return bytes(out)
