from __future__ import annotations

import base64
import logging

from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    SpeechTranscribeRequest,
    SpeechTranscribeResponse,
    SpeechTTSRequest,
    SpeechTTSResponse,
)
from backend.services.tts_service import TTSService
from backend.services.whisper_service import WhisperService
from backend.utils.audio_utils import decode_base64_audio
from backend.utils.common import safe_language

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/transcribe", response_model=SpeechTranscribeResponse)
async def transcribe(request: SpeechTranscribeRequest) -> SpeechTranscribeResponse:
    """Transcribe speech to text using faster-whisper."""

    try:
        audio = decode_base64_audio(request.audio)
        service = WhisperService()
        text, detected = await service.transcribe(audio, request.language)
        return SpeechTranscribeResponse(text=text, detected_language=detected)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Transcribe failed")
        raise HTTPException(status_code=500, detail="Failed to transcribe")


@router.post("/tts", response_model=SpeechTTSResponse)
async def tts(request: SpeechTTSRequest) -> SpeechTTSResponse:
    """Convert text to speech and return base64 MP3."""

    try:
        lang = safe_language(request.language)
        service = TTSService()
        mp3 = await service.synthesize(request.text, lang)
        return SpeechTTSResponse(audio_base64=base64.b64encode(mp3).decode("utf-8"), language=lang)
    except Exception:
        logger.exception("TTS failed")
        raise HTTPException(status_code=500, detail="Failed to synthesize speech")
