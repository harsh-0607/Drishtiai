from __future__ import annotations

import asyncio
import io
from typing import List, Tuple

import numpy as np
from PIL import Image


class YoloService:
    """YOLOv8 obstacle detection service using Ultralytics.

    Uses a lightweight model by default (yolov8n).
    """

    def __init__(self, model_name: str = "yolov8n.pt") -> None:
        self._model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(self._model_name)
        return self._model

    async def detect(self, image_bytes: bytes) -> List[Tuple[str, float, str]]:
        """Detect obstacles.

        Returns list of tuples (label, confidence, position)
        where position is left/center/right.
        """

        def _sync_detect() -> List[Tuple[str, float, str]]:
            model = self._load_model()

            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            w, h = img.size
            results = model.predict(img, verbose=False)

            out: List[Tuple[str, float, str]] = []
            for r in results:
                if r.boxes is None:
                    continue
                boxes = r.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = xyxy
                    cx = (x1 + x2) / 2.0
                    if cx < w / 3:
                        pos = "left"
                    elif cx > 2 * w / 3:
                        pos = "right"
                    else:
                        pos = "center"
                    label = r.names.get(cls, str(cls))
                    out.append((label, conf, pos))

            # sort highest confidence first
            out.sort(key=lambda t: t[1], reverse=True)
            return out[:10]

        return await asyncio.to_thread(_sync_detect)
