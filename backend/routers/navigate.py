from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.models.schemas import NavigateRequest, NavigateResponse, Obstacle
from backend.services.yolo_service import YoloService
from backend.utils.image_utils import decode_base64_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/navigate", tags=["navigate"])


@router.post("/obstacles", response_model=NavigateResponse)
async def obstacles(request: NavigateRequest) -> NavigateResponse:
    """Detect obstacles using YOLOv8."""

    try:
        img = decode_base64_image(request.image)
        service = YoloService()
        detections = await service.detect(img)

        obstacles = []
        for label, conf, pos in detections:
            obstacles.append(
                Obstacle(
                    object=label,
                    confidence=conf,
                    position=pos,
                    distance="unknown",
                )
            )

        return NavigateResponse(obstacles=obstacles)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("YOLO obstacle detection failed")
        raise HTTPException(status_code=500, detail="Failed to detect obstacles")
