import unittest
from config.settings import settings
from desktop.mouse import mouse_controller
from desktop.keyboard import keyboard_controller
from system.info import system_info_provider
from utils.security import security_guard
from fastapi import HTTPException

class TestDesktopEngine(unittest.TestCase):

    def test_settings_loaded(self):
        assert settings.app_name == "KIRA AI Desktop Control Engine"
        assert settings.version == "1.0.0"

    def test_mouse_position_returns_tuple(self):
        pos = mouse_controller.get_position()
        assert isinstance(pos, tuple)
        assert len(pos) == 2

    def test_system_info_metrics(self):
        metrics = system_info_provider.get_system_metrics()
        assert "cpu" in metrics
        assert "ram" in metrics
        assert "os" in metrics

    def test_security_guard_confirmation(self):
        with self.assertRaises(HTTPException) as cm:
            security_guard.verify_action_confirmation("file_delete", confirmed=False)
        assert cm.exception.status_code == 403

        security_guard.verify_action_confirmation("file_delete", confirmed=True)

if __name__ == "__main__":
    unittest.main()
