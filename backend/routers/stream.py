from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.database.redis_cache import get_redis
from backend.services.gemini_service import GeminiService
from backend.services.yolo_service import YoloService
from backend.services.face_service import FaceService
from backend.database.mongodb import get_mongo_db
from backend.utils.common import safe_language, sha256_bytes

logger = logging.getLogger(__name__)

router = APIRouter(tags=["stream"])


@router.websocket("/ws/stream")
async def ws_stream(
    websocket: WebSocket,
    language: str = Query(default="hi"),
    user_id: Optional[str] = Query(default=None),
) -> None:
    """Unified streaming WebSocket.

    Receives binary JPEG frames.
    Sends JSON messages:
      {"type": "scene", "message": "...", "language": "hi"}
      {"type": "obstacle", "message": {"obstacles": [...]}}
      {"type": "face", "message": {"found": true, ...}}

    Frame skipping: single-slot buffer.
    """

    await websocket.accept()
    client = getattr(websocket, "client", None)
    lang = safe_language(language)
    logger.info("/ws/stream connected client=%s lang=%s user_id=%s", client, lang, user_id)

    latest_frame: Optional[bytes] = None
    new_frame_event = asyncio.Event()
    closed = asyncio.Event()

    gemini = GeminiService()
    yolo = YoloService()

    db = get_mongo_db()
    face = FaceService(db) if user_id else None

    r = get_redis()

    async def reader_loop() -> None:
        nonlocal latest_frame
        try:
            while True:
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    raise WebSocketDisconnect
                frame = msg.get("bytes")
                if not frame:
                    continue
                latest_frame = frame
                new_frame_event.set()
        except WebSocketDisconnect:
            logger.info("/ws/stream disconnected client=%s", client)
        except Exception:
            logger.exception("/ws/stream reader error client=%s", client)
        finally:
            closed.set()
            new_frame_event.set()

    async def processing_loop() -> None:
        nonlocal latest_frame
        try:
            while not closed.is_set():
                await new_frame_event.wait()
                new_frame_event.clear()
                if closed.is_set():
                    break

                frame = latest_frame
                latest_frame = None
                if not frame:
                    continue

                start = time.perf_counter()

                # Scene (cached)
                try:
                    cache_key = f"ws_scene:{lang}:{sha256_bytes(frame)}"
                    scene_text = None
                    if r is not None:
                        scene_text = await r.get(cache_key)
                    if not scene_text:
                        scene_text = await gemini.describe_scene(frame, lang)
                        if r is not None:
                            await r.set(cache_key, scene_text, ex=5)
                    await websocket.send_text(
                        json.dumps({"type": "scene", "message": scene_text, "language": lang}, ensure_ascii=False)
                    )
                except Exception:
                    logger.exception("/ws/stream scene failed")

                # Obstacles
                try:
                    det = await yolo.detect(frame)
                    obstacles = [
                        {"object": label, "confidence": conf, "position": pos, "distance": "unknown"}
                        for (label, conf, pos) in det
                    ]
                    await websocket.send_text(
                        json.dumps({"type": "obstacle", "message": {"obstacles": obstacles}}, ensure_ascii=False)
                    )
                except Exception:
                    logger.exception("/ws/stream yolo failed")

                # Face (optional)
                if face is not None and user_id:
                    try:
                        res = await face.identify_face(user_id, frame)
                        await websocket.send_text(
                            json.dumps({"type": "face", "message": res}, ensure_ascii=False)
                        )
                    except Exception:
                        logger.exception("/ws/stream face failed")

                elapsed = time.perf_counter() - start
                if elapsed > 0.5:
                    logger.debug("/ws/stream slow processing=%.3fs client=%s", elapsed, client)
        finally:
            closed.set()

    reader_task = asyncio.create_task(reader_loop())
    processor_task = asyncio.create_task(processing_loop())

    try:
        await asyncio.wait({reader_task, processor_task}, return_when=asyncio.FIRST_COMPLETED)
    finally:
        closed.set()
        for t in (reader_task, processor_task):
            t.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await t
