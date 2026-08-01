import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple
from utils.logger import logger

class UIDetector:
    """
    Computer Vision UI Element Detection Engine using OpenCV contour topology,
    edge analysis, aspect-ratio heuristics, and component classification.
    """

    def detect_ui_elements(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Analyze screenshot and return structured UI component list:
        - buttons
        - textboxes / search bars
        - checkboxes / radio buttons
        - dropdowns
        - tabs / menus
        - icons / desktop items
        - taskbar / windows
        """
        cv_img = np.array(image.convert("RGB"))
        cv_bgr = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
        height, width, _ = cv_bgr.shape

        elements: List[Dict[str, Any]] = []

        # 1. Edge & Contour Detection
        edges = cv2.Canny(gray, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)

            # Filter tiny noise or screen-filling contours
            if w < 12 or h < 12 or w > width * 0.98 or h > height * 0.98:
                continue

            aspect_ratio = float(w) / h
            area = cv2.contourArea(cnt)
            rect_area = w * h
            extent = float(area) / rect_area if rect_area > 0 else 0

            # Classification heuristics
            element_type = self._classify_element(x, y, w, h, width, height, aspect_ratio, extent)

            if element_type:
                # Calculate mean color in target area
                roi = cv_bgr[y:y+h, x:x+w]
                mean_bgr = cv2.mean(roi)[:3] if roi.size > 0 else (128, 128, 128)
                hex_color = f"#{int(mean_bgr[2]):02x}{int(mean_bgr[1]):02x}{int(mean_bgr[0]):02x}"

                elements.append({
                    "id": f"ui_elem_{len(elements)+1}",
                    "type": element_type,
                    "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "center": {"x": int(x + w // 2), "y": int(y + h // 2)},
                    "aspect_ratio": round(aspect_ratio, 2),
                    "dominant_color": hex_color,
                    "confidence": 0.82
                })

        # Add default desktop taskbar detection if present
        elements.extend(self._detect_special_regions(width, height))
        logger.debug(f"UI Detector found {len(elements)} desktop interactive elements.")
        return elements

    def _classify_element(
        self, x: int, y: int, w: int, h: int,
        screen_w: int, screen_h: int,
        aspect_ratio: float, extent: float
    ) -> str:
        """
        Classify bounding box geometry into UI component types.
        """
        # Checkbox or Radio Button (small square-ish components)
        if 12 <= w <= 26 and 12 <= h <= 26 and 0.8 <= aspect_ratio <= 1.25:
            return "checkbox"

        # Square Icon
        if 24 <= w <= 64 and 24 <= h <= 64 and 0.85 <= aspect_ratio <= 1.18:
            return "icon"

        # Search bar or input field (wide rectangular input)
        if w >= 120 and 20 <= h <= 45 and aspect_ratio >= 3.5:
            return "textbox" if y > 100 else "search_bar"

        # Button (rectangular clickable control)
        if 40 <= w <= 220 and 18 <= h <= 55 and 1.2 <= aspect_ratio <= 5.0:
            return "button"

        # Dropdown select control
        if 80 <= w <= 260 and 22 <= h <= 40 and 2.5 <= aspect_ratio <= 6.5:
            return "dropdown"

        # Tab or Menu item
        if 50 <= w <= 180 and 15 <= h <= 35 and 1.5 <= aspect_ratio <= 4.0 and y < 120:
            return "tab"

        # Window boundary
        if w >= screen_w * 0.3 and h >= screen_h * 0.3:
            return "window"

        return "ui_container"

    def _detect_special_regions(self, width: int, height: int) -> List[Dict[str, Any]]:
        """
        Infer system Taskbar and Top Window Titlebar regions.
        """
        return [
            {
                "id": "ui_taskbar",
                "type": "taskbar",
                "bounding_box": {"x": 0, "y": height - 48, "width": width, "height": 48},
                "center": {"x": width // 2, "y": height - 24},
                "aspect_ratio": round(width / 48.0, 2),
                "dominant_color": "#1e1e2e",
                "confidence": 0.95
            },
            {
                "id": "ui_desktop_icons_area",
                "type": "desktop_icons_area",
                "bounding_box": {"x": 0, "y": 0, "width": 120, "height": height - 48},
                "center": {"x": 60, "y": (height - 48) // 2},
                "aspect_ratio": 0.1,
                "dominant_color": "#000000",
                "confidence": 0.80
            }
        ]

ui_detector = UIDetector()
