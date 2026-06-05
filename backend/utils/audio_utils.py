from __future__ import annotations

import base64


def decode_base64_audio(audio_b64: str) -> bytes:
    """Decode a base64 string (optionally with data URL prefix) into bytes."""

    if not audio_b64:
        raise ValueError("audio is required")

    if "," in audio_b64 and audio_b64.strip().lower().startswith("data:"):
        audio_b64 = audio_b64.split(",", 1)[1]

    return base64.b64decode(audio_b64, validate=True)
