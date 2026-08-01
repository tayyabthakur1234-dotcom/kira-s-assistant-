import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, List, Tuple
from vision.ocr_engine import ocrengine
from vision.ui_detector import ui_detector
from utils.logger import logger

class VisualSearchEngine:
    """
    Multimodal Visual Search & Spatial Object Locator.
    Finds UI elements, text, buttons, icons, image templates, colors, and closest matching objects on screen.
    """

    def find_button(self, image: Image.Image, text: str) -> Dict[str, Any]:
        """
        Find button on screen matching specific text label.
        """
        clean_text = text.strip().lower()
        # Step 1: Run OCR to scan text labels
        ocr_items = ocrengine.extract_text(image)
        for item in ocr_items:
            item_text = item["text"].strip().lower()
            if clean_text in item_text or item_text in clean_text:
                center = item["center"]
                bbox = item["bounding_box"]
                logger.info(f"VisualSearch: Found button '{text}' via OCR at ({center['x']}, {center['y']})")
                return {
                    "found": True,
                    "target": text,
                    "x": center["x"],
                    "y": center["y"],
                    "bounding_box": bbox,
                    "confidence": item["confidence"],
                    "method": "ocr_text_match"
                }

        # Step 2: Fallback to UI element detector
        ui_elems = ui_detector.detect_ui_elements(image)
        for elem in ui_elems:
            if elem["type"] == "button":
                center = elem["center"]
                return {
                    "found": True,
                    "target": text,
                    "x": center["x"],
                    "y": center["y"],
                    "bounding_box": elem["bounding_box"],
                    "confidence": 0.65,
                    "method": "ui_element_heuristic"
                }

        return {
            "found": False,
            "target": text,
            "x": 0,
            "y": 0,
            "bounding_box": None,
            "confidence": 0.0,
            "method": "none"
        }

    def find_text(self, image: Image.Image, query: str) -> Dict[str, Any]:
        """
        Locate exact or fuzzy text match anywhere on screen.
        """
        clean_query = query.strip().lower()
        ocr_items = ocrengine.extract_text(image)

        best_match = None
        highest_score = 0.0

        for item in ocr_items:
            item_text = item["text"].strip().lower()
            if clean_query in item_text or item_text in clean_query:
                # Calculate simple containment confidence score
                score = len(clean_query) / max(1, len(item_text))
                if score > highest_score:
                    highest_score = score
                    best_match = item

        if best_match:
            center = best_match["center"]
            return {
                "found": True,
                "text": best_match["text"],
                "x": center["x"],
                "y": center["y"],
                "bounding_box": best_match["bounding_box"],
                "confidence": best_match["confidence"],
                "method": "ocr_text"
            }

        return {"found": False, "text": query, "x": 0, "y": 0, "confidence": 0.0}

    def find_image_template(self, main_image: Image.Image, template_image: Image.Image, threshold: float = 0.8) -> Dict[str, Any]:
        """
        OpenCV Template Matching to locate small image asset or icon on screen.
        """
        main_cv = np.array(main_image.convert("RGB"))[:, :, ::-1] # RGB to BGR
        template_cv = np.array(template_image.convert("RGB"))[:, :, ::-1]

        t_h, t_w, _ = template_cv.shape

        res = cv2.matchTemplate(main_cv, template_cv, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            top_left = max_loc
            center_x = top_left[0] + t_w // 2
            center_y = top_left[1] + t_h // 2
            return {
                "found": True,
                "x": center_x,
                "y": center_y,
                "bounding_box": {"x": top_left[0], "y": top_left[1], "width": t_w, "height": t_h},
                "confidence": round(float(max_val), 3),
                "method": "opencv_template_matching"
            }

        return {"found": False, "x": 0, "y": 0, "confidence": round(float(max_val), 3)}

    def find_icon(self, image: Image.Image, icon_name: str) -> Dict[str, Any]:
        """
        Locate icon on screen by checking UI element detector and OCR labels.
        """
        ui_elems = ui_detector.detect_ui_elements(image)
        for elem in ui_elems:
            if elem["type"] == "icon":
                center = elem["center"]
                return {
                    "found": True,
                    "icon": icon_name,
                    "x": center["x"],
                    "y": center["y"],
                    "bounding_box": elem["bounding_box"],
                    "confidence": 0.78,
                    "method": "ui_icon_detector"
                }

        # Fallback search as text
        return self.find_text(image, icon_name)

    def find_color(self, image: Image.Image, hex_color: str) -> Dict[str, Any]:
        """
        Locate area matching target HEX color code.
        """
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        cv_img = np.array(image.convert("RGB"))
        lower_bound = np.array([max(0, r - 20), max(0, g - 20), max(0, b - 20)])
        upper_bound = np.array([min(255, r + 20), min(255, g + 20), min(255, b + 20)])

        mask = cv2.inRange(cv_img, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return {
                "found": True,
                "color": hex_color,
                "x": x + w // 2,
                "y": y + h // 2,
                "bounding_box": {"x": x, "y": y, "width": w, "height": h},
                "confidence": 0.85,
                "method": "color_mask"
            }

        return {"found": False, "color": hex_color, "x": 0, "y": 0, "confidence": 0.0}

    def find_closest_object(self, image: Image.Image, target_class: str, near_x: int, near_y: int) -> Dict[str, Any]:
        """
        Find UI object of target_class closest to coordinate (near_x, near_y).
        """
        ui_elems = ui_detector.detect_ui_elements(image)
        filtered = [e for e in ui_elems if e["type"] == target_class or target_class == "any"]

        if not filtered:
            return {"found": False, "x": 0, "y": 0, "confidence": 0.0}

        def dist(e):
            cx, cy = e["center"]["x"], e["center"]["y"]
            return ((cx - near_x) ** 2 + (cy - near_y) ** 2) ** 0.5

        closest = min(filtered, key=dist)
        return {
            "found": True,
            "type": closest["type"],
            "x": closest["center"]["x"],
            "y": closest["center"]["y"],
            "bounding_box": closest["bounding_box"],
            "confidence": closest["confidence"],
            "method": "euclidean_proximity"
        }

visual_search_engine = VisualSearchEngine()
