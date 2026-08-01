from PIL import Image
from typing import Dict, Any, List
from vision.ocr_engine import ocrengine
from vision.ui_detector import ui_detector
from utils.logger import logger

class ErrorUnderstandingEngine:
    """
    Error Popup & System Exception Intelligence Engine.
    Parses Windows modal dialogs, error icons, stack traces, compiler output, and HTTP error codes visible on screen.
    Provides diagnostic root-cause explanation and suggested automated resolution steps.
    """

    ERROR_KEYWORDS = [
        "error", "failed", "exception", "fatal", "denied", "access denied",
        "permission", "not found", "404", "500", "syntaxerror", "typeerror",
        "warning", "crash", "stopped working", "retry", "abort"
    ]

    def analyze_errors(self, image: Image.Image) -> Dict[str, Any]:
        """
        Scan screenshot for error popups, dialog boxes, and error messages.
        """
        ocr_items = ocrengine.extract_text(image)
        ui_elems = ui_detector.detect_ui_elements(image)

        detected_errors: List[Dict[str, Any]] = []

        for item in ocr_items:
            text = item["text"]
            text_lower = text.lower()

            matching_keywords = [kw for kw in self.ERROR_KEYWORDS if kw in text_lower]
            if matching_keywords:
                detected_errors.append({
                    "text": text,
                    "keyword_matched": matching_keywords[0],
                    "bounding_box": item["bounding_box"],
                    "center": item["center"],
                    "confidence": item["confidence"]
                })

        has_error = len(detected_errors) > 0
        explanation = "No visible error popups or failure messages detected."
        suggested_fix = "System operating normally."

        if has_error:
            primary_msg = " ".join([e["text"] for e in detected_errors[:3]])
            explanation = f"Detected visual error on screen: '{primary_msg[:120]}'"

            if "access denied" in primary_msg.lower() or "permission" in primary_msg.lower():
                suggested_fix = "Run application as Administrator or check Windows folder security permissions."
            elif "not found" in primary_msg.lower() or "404" in primary_msg.lower():
                suggested_fix = "Verify target file path, URL spelling, or environment configuration."
            elif "syntaxerror" in primary_msg.lower() or "typeerror" in primary_msg.lower():
                suggested_fix = "Inspect syntax near reported code line and resolve parameter type mismatch."
            else:
                suggested_fix = "Click 'OK' / 'Dismiss' button or review system log details for troubleshooting."

        return {
            "has_error": has_error,
            "error_count": len(detected_errors),
            "detected_error_snippets": detected_errors,
            "explanation": explanation,
            "suggested_fix": suggested_fix
        }

error_understanding_engine = ErrorUnderstandingEngine()
