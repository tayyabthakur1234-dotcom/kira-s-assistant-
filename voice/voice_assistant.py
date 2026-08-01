import time
import asyncio
import numpy as np
from typing import Dict, Any, Optional
from voice.audio_input import audio_capture_engine
from voice.wakeword import wakeword_detector
from voice.stt_engine import stt_engine
from voice.tts_engine import tts_engine
from voice.interruption import interruption_manager
from voice.command_router import command_router
from config.settings import settings
from utils.logger import logger


class VoiceAssistantOrchestrator:
    """
    JARVIS-like Always-On Real-Time Voice Assistant Engine for KIRA AI OS.
    Manages continuous background microphone stream, wake word detection ('Hey Kira'),
    streaming VAD speech capture, STT transcription, automatic command routing,
    streaming TTS playback, and instant barge-in interruption handling.
    """

    STATE_MUTED = "muted"
    STATE_IDLE = "idle"
    STATE_LISTENING = "listening"
    STATE_PROCESSING = "processing"
    STATE_SPEAKING = "speaking"

    def __init__(self):
        self.state = self.STATE_IDLE
        self.is_active = False
        self._loop_task: Optional[asyncio.Task] = None
        self.wake_word = settings.wake_word
        self.last_activated_time: float = 0.0
        self.conversation_history = []

    def get_status(self) -> Dict[str, Any]:
        """Returns current Voice Assistant status."""
        return {
            "status": "success",
            "state": self.state,
            "is_active": self.is_active,
            "wake_word": wakeword_detector.wake_word,
            "wake_sensitivity": wakeword_detector.sensitivity,
            "voice_profile": tts_engine.active_profile,
            "is_speaking": tts_engine.is_speaking,
            "last_active": self.last_activated_time
        }

    def start(self, device_index: Optional[int] = None) -> Dict[str, Any]:
        """Activates always-on voice assistant background listening loop."""
        if device_index is not None:
            audio_capture_engine.select_device(device_index)

        self.is_active = True
        self.state = self.STATE_IDLE
        logger.info("[VoiceAssistant] Always-on JARVIS voice loop started.")
        return self.get_status()

    def stop(self) -> Dict[str, Any]:
        """Deactivates/mutes voice assistant background listening loop."""
        self.is_active = False
        self.state = self.STATE_MUTED
        tts_engine.stop_speaking()
        logger.info("[VoiceAssistant] Voice loop stopped / muted.")
        return self.get_status()

    def set_wakeword(self, wake_word: str, sensitivity: float = 0.5) -> Dict[str, Any]:
        """Configures active wake word and detection sensitivity."""
        res = wakeword_detector.set_wake_word(wake_word, sensitivity)
        self.wake_word = wake_word
        return res

    async def listen_and_transcribe(self, duration_seconds: float = 3.0) -> Dict[str, Any]:
        """Manually records microphone input and returns transcribed text."""
        self.state = self.STATE_LISTENING
        audio_data = await audio_capture_engine.record_chunks_async(duration_seconds)

        self.state = self.STATE_PROCESSING
        stt_res = stt_engine.transcribe_audio(audio_data)

        self.state = self.STATE_IDLE
        return stt_res

    async def process_user_speech(self, user_text: str) -> Dict[str, Any]:
        """
        Processes transcribed user speech through CommandRouter and speaks response.
        """
        if not user_text or not user_text.strip():
            return {"status": "error", "message": "No speech detected."}

        logger.info(f"[VoiceAssistant] Processing user command: '{user_text}'")
        self.last_activated_time = time.time()
        self.state = self.STATE_PROCESSING

        # Route request across Phase 1 Desktop, Phase 2 Vision, Phase 3 Browser, or Gemini AI
        route_res = await command_router.route_and_execute(user_text)
        reply_text = route_res.get("response_text", "Command executed successfully.")

        # Stream voice output using TTS
        self.state = self.STATE_SPEAKING

        # Set up interruption listener callback
        interruption_manager.start_monitoring(on_interruption=lambda: logger.info("[VoiceAssistant] User interrupted!"))

        tts_res = await tts_engine.speak_text(reply_text)

        interruption_manager.stop_monitoring()
        self.state = self.STATE_IDLE

        return {
            "status": "success",
            "user_text": user_text,
            "response_text": reply_text,
            "route_result": route_res,
            "tts_result": tts_res
        }

    async def speak_direct(self, text: str, voice_profile: Optional[str] = None) -> Dict[str, Any]:
        """Directly speaks given text via TTS engine."""
        self.state = self.STATE_SPEAKING
        res = await tts_engine.speak_text(text, voice_profile=voice_profile)
        self.state = self.STATE_IDLE
        return res

voice_assistant = VoiceAssistantOrchestrator()
