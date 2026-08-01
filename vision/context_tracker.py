import time
import pyautogui
from typing import Dict, Any
from windows.window_manager import window_manager
from utils.logger import logger

class ContextTracker:
    """
    Real-Time Desktop Context Tracker.
    Monitors focused window handle, application process, active task state, and user input motion.
    """

    def __init__(self):
        self._last_mouse_pos = (0, 0)
        self._last_check_time = time.time()

    def get_current_context(self) -> Dict[str, Any]:
        """
        Return snapshot of real-time desktop context.
        """
        # Active Window
        active_window = window_manager.get_active_window()

        # Mouse activity check
        try:
            curr_pos = pyautogui.position()
            mouse_moved = (curr_pos[0] != self._last_mouse_pos[0] or curr_pos[1] != self._last_mouse_pos[1])
            self._last_mouse_pos = (curr_pos[0], curr_pos[1])
        except Exception:
            curr_pos = (0, 0)
            mouse_moved = False

        return {
            "active_window": active_window,
            "mouse_position": {"x": curr_pos[0], "y": curr_pos[1]},
            "mouse_active": mouse_moved,
            "timestamp": time.time(),
            "status": "active"
        }

context_tracker = ContextTracker()
