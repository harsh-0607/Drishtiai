from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException

from backend.database.redis_cache import get_redis
from backend.models.schemas import SceneRequest, SceneResponse
from backend.services.gemini_service import GeminiService
from backend.utils.common import safe_language, sha256_bytes
from backend.utils.image_utils import decode_base64_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scene", tags=["scene"])


async def get_gemini_service() -> GeminiService:
    return GeminiService()


@router.post("/describe", response_model=SceneResponse)
async def describe_scene(
    request: SceneRequest,
    gemini: GeminiService = Depends(get_gemini_service),
):
    """Describe surroundings for a visually impaired user."""

    t0 = time.perf_counter()
    try:
        img = decode_base64_image(request.image)
        lang = safe_language(request.language)

        r = get_redis()
        cache_key = f"scene:{lang}:{sha256_bytes(img)}"
        if r is not None:
            cached = await r.get(cache_key)
            if cached:
                return SceneResponse(
                    description=cached,
                    language=lang,
                    processing_time_ms=int((time.perf_counter() - t0) * 1000),
                )

        desc = await gemini.describe_scene(img, lang)

        if r is not None:
            await r.set(cache_key, desc, ex=5)

        return SceneResponse(
            description=desc,
            language=lang,
            processing_time_ms=int((time.perf_counter() - t0) * 1000),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Scene describe failed")
        raise HTTPException(status_code=500, detail="Failed to describe scene")
