from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.scene import router as scene_ws_router
from backend.routers.scene_rest import router as scene_rest_router
from backend.routers.ocr import router as ocr_router
from backend.routers.face import router as face_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="DRISHTI AI", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(scene_ws_router)  # /ws/scene
    app.include_router(scene_rest_router)  # /api/scene/describe
    app.include_router(ocr_router)  # /api/ocr/read
    app.include_router(face_router)  # /api/face/register + /api/face/recognize

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
