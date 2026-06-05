from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SceneRequest(BaseModel):
    image: str = Field(..., description="Base64-encoded JPEG image (can be data URL)")
    language: str = Field(default="hi")


class SceneResponse(BaseModel):
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


class SpeechTranscribeRequest(BaseModel):
    audio: str = Field(..., description="Base64 encoded audio (webm/wav/mp3)")
    language: Optional[str] = Field(default=None, description="Optional hint")


class SpeechTranscribeResponse(BaseModel):
    text: str
    detected_language: Optional[str] = None


class SpeechTTSRequest(BaseModel):
    text: str
    language: str = "hi"


class SpeechTTSResponse(BaseModel):
    audio_base64: str
    language: str


class NavigateRequest(BaseModel):
    image: str


class Obstacle(BaseModel):
    object: str
    confidence: float
    position: str
    distance: str


class NavigateResponse(BaseModel):
    obstacles: list[Obstacle]


class StreamMessage(BaseModel):
    type: str
    message: Any
    language: Optional[str] = None
