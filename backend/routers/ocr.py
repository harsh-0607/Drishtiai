from __future__ import annotations

import logging
import time

from fastapi import APIRouter, HTTPException

from backend.models.schemas import OCRRequest, OCRResponse
from backend.services.ocr_service import OCRService
from backend.utils.common import safe_language, sha256_bytes
from backend.utils.image_utils import decode_base64_image
from backend.database.redis_cache import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


async def get_ocr_service() -> OCRService:
    return OCRService()


@router.post("/read", response_model=OCRResponse)
async def read_text(request: OCRRequest):
    """Read text from an image using OCR."""

    t0 = time.perf_counter()
    try:
        img = decode_base64_image(request.image)
        lang = safe_language(request.language)

        r = get_redis()
        cache_key = f"ocr:{lang}:{sha256_bytes(img)}"
        if r is not None:
            cached = await r.get(cache_key)
            if cached:
                return OCRResponse(
                    text=cached,
                    language=lang,
                    processing_time_ms=int((time.perf_counter() - t0) * 1000),
                )

        service = await get_ocr_service()
        text, confidence = await service.read_text(img, lang)

        if r is not None:
            await r.set(cache_key, text, ex=5)

        return OCRResponse(
            text=text,
            language=lang,
            confidence=confidence,
            processing_time_ms=int((time.perf_counter() - t0) * 1000),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("OCR read failed")
        raise HTTPException(status_code=500, detail="Failed to read text")
