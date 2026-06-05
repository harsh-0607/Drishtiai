from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["scene"])


async def get_gemini_service() -> GeminiService:
    """Dependency provider for GeminiService.

    Kept as a function so it can be overridden in tests.
    """

    return GeminiService()


@router.websocket("/ws/scene")
async def ws_scene(
    websocket: WebSocket,
    language: str = Query(default="hi", description="BCP-47 language code, e.g. hi, en"),
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> None:
    """Receive JPEG frames over WebSocket and return scene descriptions.

    - Expects binary messages containing a JPEG image.
    - Designed for 2fps input from the client.
    - Uses a non-blocking frame skipping strategy: if processing exceeds 0.5s,
      incoming frames are dropped while the loop is busy.
    """

    await websocket.accept()
    client = getattr(websocket, "client", None)
    logger.info("/ws/scene connected client=%s language=%s", client, language)

    # Single-slot buffer: newest frame wins. This prevents unbounded buffering.
    latest_frame: Optional[bytes] = None

    # Event signals that a new frame arrived.
    new_frame_event = asyncio.Event()

    # Used to coordinate read loop and processing loop.
    closed = asyncio.Event()

    async def reader_loop() -> None:
        nonlocal latest_frame
        try:
            while True:
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    raise WebSocketDisconnect

                frame = msg.get("bytes")
                if not frame:
                    # Ignore non-binary messages (or empty frames)
                    continue

                # Non-blocking frame skipping:
                # If processing is busy (event already set and frame not yet consumed),
                # just replace the latest frame; this effectively drops intermediate frames.
                latest_frame = frame
                new_frame_event.set()
        except WebSocketDisconnect:
            logger.info("/ws/scene disconnected client=%s", client)
        except Exception:
            logger.exception("/ws/scene reader_loop error client=%s", client)
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
                try:
                    text = await gemini_service.describe_scene(frame, language)
                    payload = {"status": "success", "text": text}
                    await websocket.send_text(json.dumps(payload, ensure_ascii=False))
                except Exception:
                    logger.exception("/ws/scene processing error client=%s", client)
                    # Keep connection alive, but inform client.
                    await websocket.send_text(
                        json.dumps(
                            {"status": "error", "text": ""},
                            ensure_ascii=False,
                        )
                    )

                elapsed = time.perf_counter() - start
                # If processing took too long, we intentionally do nothing special here;
                # the reader loop keeps only a single latest frame, so frames are dropped.
                if elapsed > 0.5:
                    logger.debug(
                        "/ws/scene slow frame processing=%.3fs client=%s (dropping intermediate frames)",
                        elapsed,
                        client,
                    )
        finally:
            closed.set()

    reader_task = asyncio.create_task(reader_loop())
    processor_task = asyncio.create_task(processing_loop())

    # Wait for either task to finish (disconnect / error)
    done, pending = await asyncio.wait(
        {reader_task, processor_task},
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

