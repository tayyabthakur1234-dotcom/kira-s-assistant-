from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
from api.models import (
    APIResponse,
    VoiceStartRequest,
    VoiceSpeakRequest,
    VoiceListenRequest,
    VoiceWakeWordRequest
)
from voice.voice_assistant import voice_assistant
from voice.tts_engine import tts_engine
from voice.wakeword import wakeword_detector
from voice.audio_input import audio_capture_engine
from utils.logger import logger

router = APIRouter(prefix="/voice", tags=["Voice Intelligence Engine"])


@router.post("/start", response_model=APIResponse)
async def start_voice_assistant(req: Optional[VoiceStartRequest] = None):
    """Activates always-on voice assistant background listening engine."""
    try:
        wake = req.wake_word if req and req.wake_word else None
        sens = req.sensitivity if req and req.sensitivity else 0.5
        dev_idx = req.device_index if req else None

        if wake:
            voice_assistant.set_wakeword(wake, sens)

        res = voice_assistant.start(device_index=dev_idx)
        return APIResponse(
            status="success",
            message="Voice assistant engine activated in background.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Failed to start voice assistant: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/stop", response_model=APIResponse)
async def stop_voice_assistant():
    """Deactivates/mutes voice assistant listening engine and stops speech."""
    try:
        res = voice_assistant.stop()
        return APIResponse(
            status="success",
            message="Voice assistant engine stopped / muted.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Failed to stop voice assistant: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/listen", response_model=APIResponse)
async def listen_microphone(req: Optional[VoiceListenRequest] = None):
    """Records microphone input for specified duration and transcribes speech to text."""
    try:
        dur = req.duration_seconds if req else 3.0
        stt_res = await voice_assistant.listen_and_transcribe(dur)

        # Automatically process speech if non-empty
        user_text = stt_res.get("text", "")
        proc_res = {}
        if user_text:
            proc_res = await voice_assistant.process_user_speech(user_text)

        return APIResponse(
            status="success",
            message="Listened and transcribed microphone input.",
            data={
                "stt": stt_res,
                "process_result": proc_res
            }
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Error in /voice/listen: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/speak", response_model=APIResponse)
async def speak_text(req: VoiceSpeakRequest):
    """Synthesizes given text string into emotional speech and plays audio."""
    try:
        if req.voice_profile or req.speed or req.pitch or req.volume:
            tts_engine.configure_voice(
                profile=req.voice_profile,
                speed=req.speed,
                pitch=req.pitch,
                volume=req.volume
            )

        res = await voice_assistant.speak_direct(req.text, voice_profile=req.voice_profile)
        return APIResponse(
            status="success",
            message="Speech synthesized and played successfully.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Error in /voice/speak: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/status", response_model=APIResponse)
async def get_voice_status():
    """Returns current voice engine state, device hardware list, and active profile."""
    try:
        status_data = voice_assistant.get_status()
        status_data["microphones"] = audio_capture_engine.list_input_devices()
        return APIResponse(
            status="success",
            message="Retrieved voice engine status.",
            data=status_data
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Error in /voice/status: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/wakeword", response_model=APIResponse)
async def configure_wakeword(req: VoiceWakeWordRequest):
    """Configures target wake word trigger string and sensitivity score."""
    try:
        res = voice_assistant.set_wakeword(req.wake_word, req.sensitivity)
        return APIResponse(
            status="success",
            message=f"Wake word updated to '{req.wake_word}' with sensitivity {req.sensitivity}.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[VoiceRouter] Error in /voice/wakeword: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.websocket("/ws")
async def voice_websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time bidirectional audio streaming & speech feedback."""
    await websocket.accept()
    logger.info("[VoiceRouter] Real-time voice WebSocket client connected.")
    try:
        while True:
            msg = await websocket.receive_text()
            # Process real-time voice streaming frame or prompt
            proc_res = await voice_assistant.process_user_speech(msg)
            await websocket.send_json({
                "type": "speech_response",
                "data": proc_res
            })
    except WebSocketDisconnect:
        logger.info("[VoiceRouter] Voice WebSocket disconnected.")
    except Exception as ex:
        logger.error(f"[VoiceRouter] WebSocket error: {ex}")
