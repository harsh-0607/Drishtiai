from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.database.mongodb import get_mongo_db
from backend.models.schemas import (
    FaceRegisterRequest,
    FaceRegisterResponse,
    FaceRecognizeRequest,
    FaceRecognizeResponse,
)
from backend.services.face_service import FaceService
from backend.utils.image_utils import decode_base64_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/face", tags=["face"])


@router.post("/register", response_model=FaceRegisterResponse)
async def register_face(request: FaceRegisterRequest):
    """Register a face embedding for a user."""

    try:
        img = decode_base64_image(request.image)
        db = get_mongo_db()
        service = FaceService(db)

        ok = await service.register_face(request.user_id, request.name, img)
        if not ok:
            raise HTTPException(status_code=400, detail="No face found in image")
        return FaceRegisterResponse(status="registered")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Face register failed")
        raise HTTPException(status_code=500, detail="Failed to register face")


@router.post("/recognize", response_model=FaceRecognizeResponse)
async def recognize_face(request: FaceRecognizeRequest):
    """Recognize a registered face for a user."""

    try:
        img = decode_base64_image(request.image)
        db = get_mongo_db()
        service = FaceService(db)

        result = await service.identify_face(request.user_id, img)
        if not result.get("found"):
            return FaceRecognizeResponse(found=False)

        return FaceRecognizeResponse(
            found=True,
            name=result.get("name"),
            distance=result.get("distance"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Face recognize failed")
        raise HTTPException(status_code=500, detail="Failed to recognize face")
