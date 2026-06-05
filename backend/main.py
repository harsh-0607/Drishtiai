from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.middleware.auth import FirebaseAuthMiddleware
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.routers.face import router as face_router
from backend.routers.navigate import router as navigate_router
from backend.routers.ocr import router as ocr_router
from backend.routers.scene import router as scene_ws_router
from backend.routers.scene_rest import router as scene_rest_router
from backend.routers.speech import router as speech_router
from backend.routers.stream import router as stream_ws_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="DRISHTI AI", version="0.3.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    app.add_middleware(FirebaseAuthMiddleware)

    app.include_router(scene_ws_router)  # /ws/scene
    app.include_router(stream_ws_router)  # /ws/stream

    app.include_router(scene_rest_router)
    app.include_router(ocr_router)
    app.include_router(face_router)
    app.include_router(speech_router)
    app.include_router(navigate_router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
