import os
import time
import base64
import io
from typing import List, Dict, Any, Optional
from utils.logger import logger

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None

try:
    import mss
except ImportError:
    mss = None

try:
    from PIL import Image
except ImportError:
    Image = None


class DisplayManager:
    """
    Display & Multi-Monitor Engine for resolution queries, monitor bounds,
    high-speed multi-monitor screenshot capture, and screen recording interfaces.
    """

    def get_monitors_info(self) -> List[Dict[str, Any]]:
        """Returns resolution and coordinate bounds for all connected physical display monitors."""
        monitors_data = []

        if get_monitors:
            try:
                for idx, m in enumerate(get_monitors()):
                    monitors_data.append({
                        "id": idx,
                        "name": getattr(m, "name", f"Monitor_{idx}"),
                        "x": m.x,
                        "y": m.y,
                        "width": m.width,
                        "height": m.height,
                        "is_primary": getattr(m, "is_primary", idx == 0)
                    })
                return monitors_data
            except Exception as e:
                logger.warning(f"[DisplayManager] screeninfo error: {e}")

        # Fallback using mss or default
        if mss:
            with mss.mss() as sct:
                for idx, m in enumerate(sct.monitors[1:], start=1):
                    monitors_data.append({
                        "id": idx,
                        "name": f"Display_{idx}",
                        "x": m["left"],
                        "y": m["top"],
                        "width": m["width"],
                        "height": m["height"],
                        "is_primary": idx == 1
                    })
                return monitors_data

        return [{"id": 0, "name": "Primary Display", "x": 0, "y": 0, "width": 1920, "height": 1080, "is_primary": True}]

    def take_screenshot(self, monitor_index: int = 0, region: Optional[Dict[str, int]] = None, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Captures screenshot of full display or bounding box region.
        Returns base64 PNG payload along with metadata.
        """
        logger.info(f"[DisplayManager] Capturing screenshot (monitor={monitor_index}, region={region})")

        if mss:
            with mss.mss() as sct:
                # monitor_index 0 in mss is all monitors combined; 1 is first monitor
                target_mon = sct.monitors[monitor_index + 1] if (monitor_index + 1) < len(sct.monitors) else sct.monitors[1]
                
                if region:
                    capture_bounds = {
                        "top": region.get("top", target_mon["top"]),
                        "left": region.get("left", target_mon["left"]),
                        "width": region.get("width", target_mon["width"]),
                        "height": region.get("height", target_mon["height"])
                    }
                else:
                    capture_bounds = target_mon

                sct_img = sct.grab(capture_bounds)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX") if Image else None

                b64_str = ""
                if img:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    if save_path:
                        img.save(save_path)

                return {
                    "status": "success",
                    "width": capture_bounds["width"],
                    "height": capture_bounds["height"],
                    "saved_path": save_path,
                    "image_base64_png": b64_str
                }

        # Simulation fallback image
        if Image:
            dummy_img = Image.new('RGB', (1920, 1080), color=(30, 30, 30))
            buffered = io.BytesIO()
            dummy_img.save(buffered, format="PNG")
            b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return {"status": "simulated", "width": 1920, "height": 1080, "image_base64_png": b64_str}

        return {"status": "error", "message": "No screenshot backend available (mss / Pillow)"}

    def capture_screen_sequence(self, duration_sec: float = 2.0, fps: int = 5) -> Dict[str, Any]:
        """Captures a rapid frame sequence for short screen recording interface."""
        frames = []
        interval = 1.0 / fps
        start_time = time.time()

        while (time.time() - start_time) < duration_sec:
            frame_res = self.take_screenshot(monitor_index=0)
            if frame_res.get("status") == "success":
                frames.append(frame_res["image_base64_png"])
            time.sleep(interval)

        return {
            "status": "success",
            "frames_captured": len(frames),
            "fps": fps,
            "duration_sec": duration_sec
        }


display_manager = DisplayManager()
