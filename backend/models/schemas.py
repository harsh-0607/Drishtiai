from __future__ import annotations

import time
from typing import Optional

from pydantic import BaseModel, Field


class SceneRequest(BaseModel):
    """Request model for scene description."""

    image: str = Field(..., description="Base64-encoded JPEG image (can be data URL)")
    language: str = Field(default="hi", description="Language code (hi, en, ta, te, ...) ")


class SceneResponse(BaseModel):
    """Response model for scene description."""

    description: str
    language: str
    processing_time_ms: Optional[int] = None


class OCRRequest(BaseModel):
    image: str
    language: str = "hi"


class OCRResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None


class FaceRegisterRequest(BaseModel):
    user_id: str
    name: str
    image: str


class FaceRegisterResponse(BaseModel):
    status: str


class FaceRecognizeRequest(BaseModel):
    user_id: str
    image: str


class FaceRecognizeResponse(BaseModel):
    found: bool
    name: Optional[str] = None
    distance: Optional[float] = None
