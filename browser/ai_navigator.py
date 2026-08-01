from typing import Dict, Any, Optional
from PIL import Image
import io
from browser.engine import browser_engine
from vision.capture import screen_capture_engine
from vision.click_target import click_target_resolver
from vision.gemini_vision import gemini_vision_engine
from utils.logger import logger

class AIBrowserNavigator:
    """
    Autonomous AI Browser Navigation & Visual Fallback Engine.
    When Playwright DOM selectors fail, time out, or encounter shadow-DOM / canvas elements,
    the engine captures page screenshots, invokes Phase 2 Vision Engine & Gemini Vision,
    resolves element coordinates, and delegates mouse execution to Phase 1 Desktop Engine!
    """

    async def click_with_fallback(
        self,
        selector: str,
        visual_label: Optional[str] = None,
        timeout_ms: int = 5000
    ) -> Dict[str, Any]:
        """
        Attempts standard Playwright DOM click. If selector fails, initiates Phase 2 Vision fallback.
        """
        visual_target = visual_label or selector.replace('#', '').replace('.', '')

        # Attempt 1: Playwright DOM click
        try:
            page = await browser_engine.get_active_page()
            logger.info(f"[AINavigator] Attempting DOM click for selector: '{selector}'")
            await page.click(selector, timeout=timeout_ms)
            return {
                "status": "success",
                "method": "playwright_dom",
                "selector": selector
            }
        except Exception as dom_err:
            logger.warning(f"[AINavigator] DOM click failed for '{selector}': {dom_err}. Launching Phase 2 Vision Engine Fallback...")

        # Attempt 2: Phase 2 Vision Engine Visual Search + Phase 1 Click
        return await self._execute_vision_fallback(visual_target)

    async def _execute_vision_fallback(self, visual_target: str) -> Dict[str, Any]:
        """Captures page screenshot and uses Phase 2 Vision Engine to resolve (X,Y) and click."""
        try:
            # 1. Capture current desktop / browser screenshot
            page = await browser_engine.get_active_page()
            png_bytes = await page.screenshot(type="png")
            img = Image.open(io.BytesIO(png_bytes))

            # 2. Invoke Phase 2 Click Target Resolver
            resolution = click_target_resolver.resolve_and_click(
                target=visual_target,
                target_type="button",
                image=img,
                execute_click=True
            )

            if resolution.get("found"):
                logger.info(f"[AINavigator] Vision Fallback succeeded! Clicked '{visual_target}' at ({resolution['x']}, {resolution['y']}).")
                return {
                    "status": "success",
                    "method": "vision_engine_fallback",
                    "target": visual_target,
                    "x": resolution["x"],
                    "y": resolution["y"],
                    "confidence": resolution["confidence"]
                }
            else:
                # 3. Last Resort: Ask Gemini Vision for recommended coordinate action
                gemini_res = gemini_vision_engine.analyze_screen(
                    img,
                    prompt=f"Where is the '{visual_target}' element or button located on screen? Return x, y center coordinates."
                )
                buttons = gemini_res.get("buttons", [])
                if buttons:
                    b = buttons[0]
                    target_x = b.get("x", 100)
                    target_y = b.get("y", 100)

                    # Execute click via Click Target Resolver
                    from desktop.mouse import mouse_controller
                    mouse_res = mouse_controller.click(x=target_x, y=target_y)

                    return {
                        "status": "success",
                        "method": "gemini_vision_coordinate_fallback",
                        "target": visual_target,
                        "x": target_x,
                        "y": target_y,
                        "click_details": mouse_res
                    }

            return {
                "status": "error",
                "message": f"Could not locate '{visual_target}' via DOM or Vision Engine.",
                "target": visual_target
            }

        except Exception as e:
            logger.error(f"[AINavigator] Vision fallback failed: {e}")
            return {"status": "error", "message": str(e), "target": visual_target}

ai_browser_navigator = AIBrowserNavigator()
