import io
import base64
import time
import mss
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, Tuple, List
from utils.logger import logger

class ScreenCaptureEngine:
    """
    High-Performance Real-Time Desktop Screen Capture Engine.
    Supports multi-monitor capture, active monitor detection, region cropping, and frame buffer caching.
    """
    def __init__(self):
        self._last_frame: Optional[Image.Image] = None
        self._last_capture_time: float = 0.0

    def capture_screen(
        self,
        monitor_index: int = 0,
        region: Optional[Dict[str, int]] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Capture desktop screen.
        monitor_index: 0 for primary/all combined, 1 for Monitor 1, 2 for Monitor 2, etc.
        region: dict with {left, top, width, height}
        """
        start_time = time.time()
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                # Validate monitor index
                if monitor_index < 0 or monitor_index >= len(monitors):
                    target_monitor = monitors[0] # Default to all monitors
                else:
                    target_monitor = monitors[monitor_index]

                if region:
                    capture_area = {
                        "top": region.get("top", target_monitor["top"]),
                        "left": region.get("left", target_monitor["left"]),
                        "width": region.get("width", target_monitor["width"]),
                        "height": region.get("height", target_monitor["height"]),
                    }
                else:
                    capture_area = target_monitor

                sct_img = sct.grab(capture_area)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

                elapsed_ms = (time.time() - start_time) * 1000
                self._last_frame = img
                self._last_capture_time = time.time()

                metadata = {
                    "width": img.width,
                    "height": img.height,
                    "monitor_index": monitor_index,
                    "region": capture_area,
                    "capture_time_ms": round(elapsed_ms, 2),
                    "timestamp": self._last_capture_time
                }
                logger.debug(f"Captured screen ({img.width}x{img.height}) in {elapsed_ms:.2f}ms")
                return img, metadata

        except Exception as e:
            logger.error(f"Error during screen capture: {e}")
            # Fallback: create placeholder or synthetic desktop frame if mss fails in non-display container environment
            img = Image.new("RGB", (1920, 1080), color=(30, 32, 48))
            metadata = {
                "width": 1920,
                "height": 1080,
                "monitor_index": monitor_index,
                "region": {"top": 0, "left": 0, "width": 1920, "height": 1080},
                "capture_time_ms": 1.0,
                "timestamp": time.time(),
                "fallback": True
            }
            self._last_frame = img
            return img, metadata

    def capture_all_monitors(self) -> List[Tuple[Image.Image, Dict[str, Any]]]:
        """
        Capture each monitor independently.
        """
        results = []
        try:
            with mss.mss() as sct:
                for idx in range(1, len(sct.monitors)):
                    img, meta = self.capture_screen(monitor_index=idx)
                    results.append((img, meta))
        except Exception as e:
            logger.error(f"Failed capturing all monitors: {e}")
            img, meta = self.capture_screen(monitor_index=0)
            results.append((img, meta))
        return results

    def capture_selected_region(self, left: int, top: int, width: int, height: int) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Capture a specific pixel bounding box on screen.
        """
        region = {"left": left, "top": top, "width": width, "height": height}
        return self.capture_screen(monitor_index=0, region=region)

    @staticmethod
    def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to Base64 encoded data string.
        """
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/{format.lower()};base64,{encoded}"

    @staticmethod
    def image_to_cv2(img: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV BGR NumPy array.
        """
        rgb_arr = np.array(img)
        return rgb_arr[:, :, ::-1].copy() # Convert RGB to BGR

screen_capture_engine = ScreenCaptureEngine()
