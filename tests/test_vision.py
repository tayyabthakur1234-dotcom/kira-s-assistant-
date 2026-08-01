import unittest
from PIL import Image
from vision.capture import screen_capture_engine
from vision.ocr_engine import ocrengine
from vision.ui_detector import ui_detector
from vision.gemini_vision import gemini_vision_engine
from vision.visual_search import visual_search_engine
from vision.click_target import click_target_resolver
from vision.app_intelligence import app_intelligence
from vision.error_understanding import error_understanding_engine
from vision.context_tracker import context_tracker

class TestVisionEngine(unittest.TestCase):

    def test_screen_capture_returns_image_and_metadata(self):
        img, meta = screen_capture_engine.capture_screen()
        assert isinstance(img, Image.Image)
        assert meta["width"] > 0
        assert meta["height"] > 0

    def test_ocr_engine_returns_list(self):
        img = Image.new("RGB", (300, 100), color=(255, 255, 255))
        ocr_results = ocrengine.extract_text(img)
        assert isinstance(ocr_results, list)

    def test_ui_detector_elements(self):
        img = Image.new("RGB", (800, 600), color=(50, 50, 50))
        ui_elements = ui_detector.detect_ui_elements(img)
        assert isinstance(ui_elements, list)
        assert len(ui_elements) >= 2

    def test_gemini_vision_fallback_schema(self):
        img = Image.new("RGB", (600, 400), color=(30, 30, 30))
        res = gemini_vision_engine.analyze_screen(img, prompt="What is visible?")
        assert "description" in res
        assert "buttons" in res
        assert "text" in res
        assert "windows" in res
        assert "recommended_action" in res

    def test_visual_search_find_button(self):
        img = Image.new("RGB", (600, 400), color=(240, 240, 240))
        res = visual_search_engine.find_button(img, "Submit")
        assert "found" in res
        assert "confidence" in res

    def test_click_target_resolver(self):
        res = click_target_resolver.resolve_and_click(
            target="OK",
            target_type="button",
            execute_click=False
        )
        assert "found" in res
        assert "x" in res
        assert "y" in res

    def test_app_intelligence_layout(self):
        img = Image.new("RGB", (1280, 720), color=(40, 40, 40))
        layout = app_intelligence.analyze_app_layout(img, active_app_hint="Chrome")
        assert layout["app_name"] == "Chrome"
        assert len(layout["layout_zones"]) > 0

    def test_error_understanding_engine(self):
        img = Image.new("RGB", (400, 200), color=(255, 255, 255))
        diag = error_understanding_engine.analyze_errors(img)
        assert "has_error" in diag
        assert "suggested_fix" in diag

    def test_context_tracker(self):
        ctx = context_tracker.get_current_context()
        assert "active_window" in ctx
        assert "mouse_position" in ctx

if __name__ == "__main__":
    unittest.main()
