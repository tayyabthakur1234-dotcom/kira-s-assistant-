from PIL import Image
from typing import Dict, Any, Optional
from config.settings import settings
from vision.capture import screen_capture_engine
from vision.visual_search import visual_search_engine
from vision.gemini_vision import gemini_vision_engine
from desktop.mouse import mouse_controller
from utils.logger import logger

class ClickTargetResolver:
    """
    Automatic Click Target Locator & Execution Engine.
    Locates UI target coordinates on screen, verifies confidence threshold, and hands over (X,Y)
    to Phase 1 Desktop Control Engine for automated human-like execution.
    """

    def resolve_and_click(
        self,
        target: str,
        target_type: str = "button", # "button", "text", "icon", "prompt"
        image: Optional[Image.Image] = None,
        button: str = "left",
        execute_click: bool = True
    ) -> Dict[str, Any]:
        """
        Locate element by target label or visual query, verify confidence, and optional execute Phase 1 click.
        """
        if image is None:
            image, _ = screen_capture_engine.capture_screen()

        search_res = None

        if target_type == "button":
            search_res = visual_search_engine.find_button(image, target)
        elif target_type == "text":
            search_res = visual_search_engine.find_text(image, target)
        elif target_type == "icon":
            search_res = visual_search_engine.find_icon(image, target)
        else:
            # Prompt mode: query Gemini Vision
            gemini_res = gemini_vision_engine.analyze_screen(image, prompt=f"Where is the {target}? Return its coordinates.")
            buttons = gemini_res.get("buttons", [])
            if buttons:
                b = buttons[0]
                search_res = {
                    "found": True,
                    "target": target,
                    "x": b.get("x", 0),
                    "y": b.get("y", 0),
                    "bounding_box": {"x": b.get("x", 0) - 20, "y": b.get("y", 0) - 10, "width": 40, "height": 20},
                    "confidence": 0.88,
                    "method": "gemini_vision_coordinates"
                }

        if not search_res or not search_res.get("found", False):
            # Fallback to general text search
            search_res = visual_search_engine.find_text(image, target)

        found = search_res.get("found", False)
        confidence = search_res.get("confidence", 0.0)
        x = search_res.get("x", 0)
        y = search_res.get("y", 0)

        click_executed = False
        execution_details = None

        if found and confidence >= settings.confidence_threshold:
            if execute_click:
                logger.info(f"ClickTargetResolver: Confidence {confidence:.2f} >= threshold {settings.confidence_threshold}. Invoking Phase 1 Mouse Engine at ({x}, {y}).")
                try:
                    # Execute click via Phase 1 Desktop Control Engine
                    click_res = mouse_controller.click(x=x, y=y, button=button)
                    click_executed = True
                    execution_details = click_res
                except Exception as e:
                    logger.error(f"Failed executing Phase 1 mouse click: {e}")
                    execution_details = {"error": str(e)}
        else:
            logger.warning(f"Click target '{target}' not clicked. Found: {found}, Confidence: {confidence:.2f}, Threshold: {settings.confidence_threshold}")

        return {
            "target": target,
            "target_type": target_type,
            "found": found,
            "x": x,
            "y": y,
            "confidence": confidence,
            "confidence_threshold": settings.confidence_threshold,
            "click_executed": click_executed,
            "execution_details": execution_details,
            "bounding_box": search_res.get("bounding_box")
        }

click_target_resolver = ClickTargetResolver()
