import asyncio
import numpy as np
from typing import Dict, Any, Optional, Callable
from voice.tts_engine import tts_engine
from voice.audio_input import audio_capture_engine
from utils.logger import logger

class InterruptionManager:
    """
    Interruption / Barge-in Manager.
    Monitors incoming microphone audio while KIRA is speaking (TTS output active).
    If human speech energy is detected, it triggers immediate speech termination,
    enabling natural JARVIS-like fluid conversations.
    """

    def __init__(self):
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.interruption_callback: Optional[Callable[[], None]] = None

    def start_monitoring(self, on_interruption: Optional[Callable[[], None]] = None):
        """Starts real-time microphone barge-in monitoring loop."""
        self.interruption_callback = on_interruption
        self.is_monitoring = True
        logger.info("[Interruption] Barge-in listener armed.")

    def stop_monitoring(self):
        """Stops barge-in monitoring."""
        self.is_monitoring = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        logger.info("[Interruption] Barge-in listener disarmed.")

    def process_audio_chunk(self, audio_chunk: np.ndarray) -> bool:
        """
        Evaluates microphone chunk during active TTS playback.
        Triggers interruption if user speech is detected.
        """
        if not tts_engine.is_speaking:
            return False

        has_speech = audio_capture_engine.detect_speech_vad(audio_chunk, threshold=0.02)
        if has_speech:
            logger.info("[Interruption] Human speech detected while KIRA was speaking! Stopping TTS...")
            tts_engine.stop_speaking()

            if self.interruption_callback:
                try:
                    self.interruption_callback()
                except Exception as ex:
                    logger.error(f"[Interruption] Callback error: {ex}")

            return True

        return False

interruption_manager = InterruptionManager()
