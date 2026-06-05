from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from google import genai

logger = logging.getLogger(__name__)


class GeminiService:
    """Scene description service powered by Google Gemini."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required to use GeminiService."
            )

        # Modern google-genai client
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-1.5-flash"

    async def describe_scene(self, image_bytes: bytes, language: str) -> str:
        """Generate a short, safety-focused scene description.

        Args:
            image_bytes: JPEG bytes for a single frame.
            language: Requested response language (BCP-47 or short code like 'hi', 'en').

        Returns:
            A concise description (2-3 sentences).
        """

        # Default language fallback choices
        req_lang = (language or "").strip() or "hi"

        system_instruction = (
            "You are the eyes of a visually impaired person in India. "
            "Describe the scene directly in front of them concisely, naturally, and accurately "
            f"in the requested language ({req_lang}). "
            "Focus strictly on immediate obstacles, paths, people, and safety hazards. "
            "Keep it under 2-3 sentences. Do not mention that you are an AI."
        )

        async def _call_gemini(lang: str) -> str:
            def _sync_generate() -> str:
                # google-genai expects image as a "Part". We can pass bytes with a MIME type.
                # Using client.models.generate_content is sync in many versions.
                resp = self._client.models.generate_content(
                    model=self._model,
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {"text": system_instruction.replace(f"({req_lang})", f"({lang})")},
                                {"inline_data": {"mime_type": "image/jpeg", "data": image_bytes}},
                            ],
                        }
                    ],
                )

                # Response text extraction
                text = getattr(resp, "text", None)
                if text:
                    return text.strip()

                # Fallback: attempt to read candidates structure
                try:
                    candidates = getattr(resp, "candidates", None) or []
                    if candidates and candidates[0].content and candidates[0].content.parts:
                        return str(candidates[0].content.parts[0].text).strip()
                except Exception:
                    pass

                return ""

            # Run sync SDK call off the event loop
            return await asyncio.to_thread(_sync_generate)

        try:
            text = await asyncio.wait_for(_call_gemini(req_lang), timeout=5.0)
            if text:
                return text
        except asyncio.TimeoutError:
            logger.warning("Gemini describe_scene timed out (lang=%s)", req_lang)
        except Exception:
            logger.exception("Gemini describe_scene failed (lang=%s)", req_lang)

        # Robust fallback: try Hindi, then English
        for fallback_lang in ("hi", "en"):
            if fallback_lang == req_lang:
                continue
            try:
                text = await asyncio.wait_for(_call_gemini(fallback_lang), timeout=5.0)
                if text:
                    return text
            except Exception:
                continue

        # If everything fails, return a safe generic message
        return (
            "माफ़ कीजिए, अभी मैं दृश्य का वर्णन नहीं कर पा रहा/रही। "
            "कृपया कैमरा स्थिर रखें और दोबारा प्रयास करें।"
            if req_lang.startswith("hi")
            else "Sorry, I couldn't describe the scene right now. Please hold the camera steady and try again."
        )
