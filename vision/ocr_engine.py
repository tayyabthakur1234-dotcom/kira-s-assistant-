import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings
from utils.logger import logger

# Try importing EasyOCR and PyTesseract gracefully
EASYOCR_AVAILABLE = False
PYTESSERACT_AVAILABLE = False

try:
    import pytesseract
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    PYTESSERACT_AVAILABLE = True
except Exception:
    PYTESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False


class OCREngine:
    """
    Robust Multi-Engine Optical Character Recognition (OCR) Engine.
    Extracts visible text, labels, button text, dialog error codes, code snippets, and Urdu/English scripts.
    """
    def __init__(self):
        self._easyocr_reader = None
        self._initialized = False

    def _init_easyocr(self, languages: Optional[List[str]] = None):
        if EASYOCR_AVAILABLE and self._easyocr_reader is None:
            try:
                langs = languages or ['en', 'ur']
                logger.info(f"Initializing EasyOCR reader with languages: {langs}")
                # gpu=False for container safety
                self._easyocr_reader = easyocr.Reader(langs, gpu=False)
            except Exception as e:
                logger.warning(f"EasyOCR initialization warning: {e}. Falling back to English or Tesseract.")
                try:
                    self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
                except Exception as ex:
                    logger.error(f"Failed to initialize EasyOCR: {ex}")
                    self._easyocr_reader = None

    def extract_text(
        self,
        image: Image.Image,
        languages: Optional[List[str]] = None,
        engine: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract structured text with bounding boxes [x, y, w, h], text string, and confidence.
        Support languages: ['en', 'ur'] or ['eng', 'urd']
        """
        chosen_engine = engine or settings.ocr_engine_preference
        cv_img = np.array(image.convert("RGB"))
        cv_bgr = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

        results: List[Dict[str, Any]] = []

        # Try EasyOCR if chosen or auto
        if (chosen_engine in ["easyocr", "auto"]) and EASYOCR_AVAILABLE:
            self._init_easyocr(languages)
            if self._easyocr_reader:
                try:
                    ocr_results = self._easyocr_reader.readtext(cv_bgr)
                    for bbox, text, prob in ocr_results:
                        if not text.strip():
                            continue
                        # bbox is [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                        x1 = int(bbox[0][0])
                        y1 = int(bbox[0][1])
                        x2 = int(bbox[2][0])
                        y2 = int(bbox[2][1])
                        w = max(1, x2 - x1)
                        h = max(1, y2 - y1)

                        results.append({
                            "text": text.strip(),
                            "confidence": round(float(prob), 3),
                            "bounding_box": {"x": x1, "y": y1, "width": w, "height": h},
                            "center": {"x": x1 + w // 2, "y": y1 + h // 2},
                            "engine": "easyocr"
                        })
                    if results:
                        return results
                except Exception as e:
                    logger.warning(f"EasyOCR run failed: {e}. Falling back to Tesseract / OpenCV text contours.")

        # Try Tesseract if chosen or fallback
        if PYTESSERACT_AVAILABLE:
            try:
                lang_str = "eng+urd" if ("ur" in (languages or []) or "urd" in (languages or [])) else "eng"
                data = pytesseract.image_to_data(image, lang=lang_str, output_type=pytesseract.Output.DICT)
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    conf = float(data['conf'][i])
                    if conf > 20 and text:
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        results.append({
                            "text": text,
                            "confidence": round(conf / 100.0, 3),
                            "bounding_box": {"x": x, "y": y, "width": w, "height": h},
                            "center": {"x": x + w // 2, "y": y + y // 2},
                            "engine": "tesseract"
                        })
                if results:
                    return results
            except Exception as e:
                logger.warning(f"Tesseract OCR failed: {e}. Executing contour text layout analysis.")

        # Heuristic / OpenCV Text Bounding Region Detection Fallback
        return self._fallback_contour_ocr(cv_bgr)

    def _fallback_contour_ocr(self, cv_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """
        Lightweight OpenCV contour analysis to find text blocks and UI text regions when OCR models are uninstalled.
        """
        results = []
        gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        idx = 1
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20 and h > 8 and w < cv_bgr.shape[1] * 0.9 and h < cv_bgr.shape[0] * 0.8:
                results.append({
                    "text": f"Detected_Text_Block_{idx}",
                    "confidence": 0.75,
                    "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "center": {"x": int(x + w // 2), "y": int(y + h // 2)},
                    "engine": "contour_layout"
                })
                idx += 1
        return results

ocr_engine = OCREngine()
