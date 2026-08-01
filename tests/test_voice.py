import unittest
import numpy as np
from fastapi.testclient import TestClient
from api.main import app
from voice.wakeword import wakeword_detector
from voice.stt_engine import stt_engine
from voice.tts_engine import tts_engine
from voice.command_router import command_router
from voice.voice_assistant import voice_assistant
from voice.interruption import interruption_manager

client = TestClient(app)


class TestVoiceEngine(unittest.IsolatedAsyncioTestCase):

    def test_wakeword_detector(self):
        res = wakeword_detector.set_wake_word("Hey Kira", sensitivity=0.6)
        assert res["status"] == "success"
        assert res["wake_word"] == "Hey Kira"
        assert res["sensitivity"] == 0.6

        audio_dummy = np.zeros(1600, dtype=np.float32)
        detection = wakeword_detector.detect(audio_dummy)
        assert "detected" in detection
        assert "score" in detection

    def test_stt_engine(self):
        audio_dummy = np.sin(np.linspace(0, 100, 16000)).astype(np.float32) * 0.1
        res = stt_engine.transcribe_audio(audio_dummy, language="en")
        assert res["status"] == "success"
        assert "text" in res
        assert "language" in res

    async def test_tts_engine(self):
        config_res = tts_engine.configure_voice(profile="female_1", speed=1.1, pitch=1.0)
        assert config_res["status"] == "success"
        assert config_res["speed"] == 1.1

        tts_res = await tts_engine.speak_text("Hello sir, KIRA voice engine online.", stream_playback=False)
        assert tts_res["status"] == "success"
        assert "latency_ms" in tts_res

        tts_engine.stop_speaking()
        assert tts_engine.is_speaking is False

    def test_command_router_classification(self):
        assert command_router.classify_intent("Open Notepad app") == "desktop_control"
        assert command_router.classify_intent("Search Google for AI news") == "browser_automation"
        assert command_router.classify_intent("Take a screenshot of my desktop") == "vision_request"
        assert command_router.classify_intent("Write a Python script to sort a list") == "coding"
        assert command_router.classify_intent("How are you doing today KIRA?") == "conversation"

    async def test_voice_assistant_orchestrator(self):
        status = voice_assistant.get_status()
        assert status["status"] == "success"
        assert "state" in status

        start_res = voice_assistant.start()
        assert start_res["is_active"] is True

        proc_res = await voice_assistant.process_user_speech("Search Google for KIRA AI")
        assert proc_res["status"] == "success"
        assert "response_text" in proc_res

        stop_res = voice_assistant.stop()
        assert stop_res["is_active"] is False

    def test_voice_api_endpoints(self):
        resp = client.post("/voice/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

        resp_ww = client.post("/voice/wakeword", json={"wake_word": "Hey Assistant", "sensitivity": 0.5})
        assert resp_ww.status_code == 200
        assert resp_ww.json()["status"] == "success"

        resp_start = client.post("/voice/start", json={"wake_word": "Hey Kira", "sensitivity": 0.5})
        assert resp_start.status_code == 200

        resp_speak = client.post("/voice/speak", json={"text": "Testing voice output", "voice_profile": "female_1"})
        assert resp_speak.status_code == 200

        resp_stop = client.post("/voice/stop")
        assert resp_stop.status_code == 200


if __name__ == "__main__":
    unittest.main()
