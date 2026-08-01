from PIL import Image
from typing import Dict, Any, List, Optional
from vision.ocr_engine import ocrengine
from vision.ui_detector import ui_detector
from utils.logger import logger

class ApplicationIntelligence:
    """
    Application Visual Layout Awareness Engine.
    Detects layout patterns, active tabs, address bars, editor panels, navigation trees, and toolbar regions
    for Chrome, VS Code, Explorer, Terminal, Discord, Spotify, Settings, Control Panel, Office Apps, and Games.
    """

    KNOWN_APPS = [
        "Chrome", "VS Code", "File Explorer", "Terminal", "Discord",
        "Spotify", "Windows Settings", "Control Panel", "Office", "Game"
    ]

    def analyze_app_layout(self, image: Image.Image, active_app_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract visual layout structural zones based on the open application.
        """
        w, h = image.size
        ocr_blocks = ocrengine.extract_text(image)
        ui_elements = ui_detector.detect_ui_elements(image)

        app_name = active_app_hint or self._infer_app_from_ocr(ocr_blocks)

        layout_zones: List[Dict[str, Any]] = []

        if "chrome" in app_name.lower() or "browser" in app_name.lower():
            layout_zones = [
                {"zone": "Tab Bar", "bounds": {"x": 0, "y": 0, "width": w, "height": 40}},
                {"zone": "Address Bar / URL", "bounds": {"x": 100, "y": 40, "width": w - 200, "height": 36}},
                {"zone": "Bookmarks Bar", "bounds": {"x": 0, "y": 76, "width": w, "height": 30}},
                {"zone": "Web Viewport", "bounds": {"x": 0, "y": 106, "width": w, "height": h - 154}},
                {"zone": "Status Bar", "bounds": {"x": 0, "y": h - 48, "width": w, "height": 48}}
            ]
        elif "code" in app_name.lower() or "vs" in app_name.lower():
            layout_zones = [
                {"zone": "Activity Bar", "bounds": {"x": 0, "y": 30, "width": 50, "height": h - 78}},
                {"zone": "Sidebar / File Tree", "bounds": {"x": 50, "y": 30, "width": 250, "height": h - 278}},
                {"zone": "Editor Tab Strip", "bounds": {"x": 300, "y": 30, "width": w - 300, "height": 35}},
                {"zone": "Code Editor Canvas", "bounds": {"x": 300, "y": 65, "width": w - 300, "height": h - 315}},
                {"zone": "Integrated Terminal / Console", "bounds": {"x": 300, "y": h - 250, "width": w - 300, "height": 202}},
                {"zone": "Status Bar", "bounds": {"x": 0, "y": h - 48, "width": w, "height": 22}}
            ]
        elif "explorer" in app_name.lower() or "folder" in app_name.lower():
            layout_zones = [
                {"zone": "Ribbon / Command Bar", "bounds": {"x": 0, "y": 30, "width": w, "height": 50}},
                {"zone": "Address Bar", "bounds": {"x": 60, "y": 80, "width": w - 260, "height": 30}},
                {"zone": "Search Box", "bounds": {"x": w - 200, "y": 80, "width": 190, "height": 30}},
                {"zone": "Navigation Pane", "bounds": {"x": 0, "y": 115, "width": 220, "height": h - 163}},
                {"zone": "File Grid Area", "bounds": {"x": 220, "y": 115, "width": w - 220, "height": h - 163}}
            ]
        elif "terminal" in app_name.lower() or "cmd" in app_name.lower() or "powershell" in app_name.lower():
            layout_zones = [
                {"zone": "Terminal Tab Header", "bounds": {"x": 0, "y": 0, "width": w, "height": 35}},
                {"zone": "CLI Output Buffer", "bounds": {"x": 0, "y": 35, "width": w, "height": h - 83}},
                {"zone": "Active Prompt Input Line", "bounds": {"x": 0, "y": h - 80, "width": w, "height": 32}}
            ]
        else:
            layout_zones = [
                {"zone": "Titlebar", "bounds": {"x": 0, "y": 0, "width": w, "height": 32}},
                {"zone": "Main Application Canvas", "bounds": {"x": 0, "y": 32, "width": w, "height": h - 80}},
                {"zone": "Taskbar", "bounds": {"x": 0, "y": h - 48, "width": w, "height": 48}}
            ]

        return {
            "app_name": app_name,
            "resolution": {"width": w, "height": h},
            "layout_zones": layout_zones,
            "ui_elements_count": len(ui_elements),
            "text_blocks_count": len(ocr_blocks)
        }

    def _infer_app_from_ocr(self, ocr_blocks: List[Dict[str, Any]]) -> str:
        text_concat = " ".join([b["text"].lower() for b in ocr_blocks])
        if "visual studio code" in text_concat or "vscode" in text_concat or ".py" in text_concat or ".tsx" in text_concat:
            return "VS Code"
        if "chrome" in text_concat or "http" in text_concat or "google" in text_concat or "tab" in text_concat:
            return "Chrome"
        if "quick access" in text_concat or "this pc" in text_concat or "documents" in text_concat:
            return "File Explorer"
        if "powershell" in text_concat or "administrator" in text_concat or "cmd.exe" in text_concat:
            return "Terminal"
        if "discord" in text_concat:
            return "Discord"
        if "spotify" in text_concat:
            return "Spotify"
        if "settings" in text_concat:
            return "Windows Settings"
        return "Generic Windows App"

app_intelligence = ApplicationIntelligence()
