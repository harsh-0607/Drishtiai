from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.scene import router as scene_router


def create_app() -> FastAPI:
    app = FastAPI(title="DRISHTI AI", version="0.1.0")

    # CORS: allow frontend dev/prod. Set FRONTEND_ORIGINS to tighten.
    origins_env = os.getenv("FRONTEND_ORIGINS", "*")
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"] ,
    )

    app.include_router(scene_router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
