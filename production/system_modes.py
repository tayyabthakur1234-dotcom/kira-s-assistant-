"""
System Execution Modes - KIRA AI Operating System (Phase 12)
Manages application execution modes:
Windows Service Mode, Portable Mode, Developer Mode, Safe Mode,
Offline Mode, Cloud Mode, and Low Resource Mode.
"""

from typing import Dict, Any, List
from utils.logger import logger


class SystemModesManager:
    def __init__(self):
        self.active_mode = "Cloud Mode"
        self.available_modes = {
            "Windows Service Mode": "Runs silently in Windows background service with system tray icon and wake word listener.",
            "Portable Mode": "Runs fully isolated from USB/directory without Windows Registry footprints.",
            "Developer Mode": "Enables verbose debug logs, hot reload API endpoints, AST inspection, and raw LLM prompt outputs.",
            "Safe Mode": "Disables custom third-party plugins and locks execution permissions to read-only.",
            "Offline Mode": "Enforces 100% local model execution (Ollama / Local Whisper / Llama 3) without internet outbound calls.",
            "Cloud Mode": "Optimized for hybrid cloud LLM routing (Gemini 2.5 Flash, Grok 3, Claude 3.5 Sonnet) with low latency.",
            "Low Resource Mode": "Caps CPU usage to <2% and memory footprint to <50MB for legacy hardware."
        }

    def set_active_mode(self, mode_name: str) -> Dict[str, Any]:
        """Switches KIRA execution mode."""
        if mode_name not in self.available_modes:
            return {
                "status": "error",
                "message": f"Unknown mode '{mode_name}'. Available: {list(self.available_modes.keys())}"
            }
        self.active_mode = mode_name
        logger.info(f"KIRA Operating System switched to mode: {mode_name}")
        return {
            "status": "success",
            "active_mode": self.active_mode,
            "description": self.available_modes[self.active_mode]
        }

    def get_mode_status(self) -> Dict[str, Any]:
        """Returns active execution mode and descriptions."""
        return {
            "status": "success",
            "active_mode": self.active_mode,
            "available_modes": self.available_modes
        }


system_modes = SystemModesManager()
