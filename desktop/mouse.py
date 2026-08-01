import time
import math
import random
from typing import Tuple, Optional, Dict, Any
from utils.logger import logger

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
except ImportError:
    pyautogui = None

try:
    import mouse as mouse_lib
except ImportError:
    mouse_lib = None


class MouseController:
    """
    Modular Mouse Control Engine capable of controlling cursor movement,
    smooth human-like trajectories, multi-button clicking, dragging, scrolling,
    and cursor position tracking.
    """

    def __init__(self, human_speed: float = 0.3):
        self.human_speed = human_speed

    def get_position(self) -> Tuple[int, int]:
        """Returns the current (x, y) coordinates of the cursor."""
        if pyautogui:
            x, y = pyautogui.position()
            return int(x), int(y)
        if mouse_lib:
            return mouse_lib.get_position()
        return (0, 0)

    def move_to(self, x: int, y: int, smooth: bool = True, duration: Optional[float] = None) -> Dict[str, Any]:
        """
        Moves the mouse cursor to target coordinates (x, y).
        Optionally uses human-like smooth ease movement.
        """
        start_x, start_y = self.get_position()
        dur = duration if duration is not None else self.human_speed

        logger.info(f"[MouseController] Moving cursor from ({start_x}, {start_y}) to ({x}, {y}) (smooth={smooth})")

        if pyautogui:
            if smooth:
                # Human-like movement with easing curve
                pyautogui.moveTo(x, y, duration=dur, tween=pyautogui.easeInOutQuad)
            else:
                pyautogui.moveTo(x, y)
        elif mouse_lib:
            mouse_lib.move(x, y, absolute=True, duration=dur if smooth else 0)
        else:
            raise RuntimeError("No mouse automation backend installed (pyautogui / mouse)")

        end_x, end_y = self.get_position()
        return {"status": "success", "from": [start_x, start_y], "to": [end_x, end_y]}

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1, interval: float = 0.1) -> Dict[str, Any]:
        """
        Executes single, double, or multi-clicks with specified button ('left', 'right', 'middle').
        """
        if x is not None and y is not None:
            self.move_to(x, y, smooth=True)

        curr_x, curr_y = self.get_position()
        logger.info(f"[MouseController] Clicking '{button}' {clicks}x at ({curr_x}, {curr_y})")

        if pyautogui:
            pyautogui.click(x=curr_x, y=curr_y, clicks=clicks, interval=interval, button=button)
        elif mouse_lib:
            for _ in range(clicks):
                mouse_lib.click(button=button)
                time.sleep(interval)
        else:
            raise RuntimeError("No mouse automation backend available")

        return {"status": "success", "button": button, "clicks": clicks, "at": [curr_x, curr_y]}

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Shortcut for double left click."""
        return self.click(x=x, y=y, button="left", clicks=2, interval=0.1)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Shortcut for single right click."""
        return self.click(x=x, y=y, button="right", clicks=1)

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, button: str = "left", duration: float = 0.5) -> Dict[str, Any]:
        """Drags from (start_x, start_y) and drops at (end_x, end_y)."""
        logger.info(f"[MouseController] Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        self.move_to(start_x, start_y, smooth=True)

        if pyautogui:
            pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        elif mouse_lib:
            mouse_lib.press(button=button)
            mouse_lib.move(end_x, end_y, absolute=True, duration=duration)
            mouse_lib.release(button=button)
        else:
            raise RuntimeError("No mouse backend available")

        return {"status": "success", "dragged_from": [start_x, start_y], "dropped_at": [end_x, end_y]}

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """
        Scrolls the mouse wheel up (positive integer) or down (negative integer).
        """
        if x is not None and y is not None:
            self.move_to(x, y, smooth=False)

        logger.info(f"[MouseController] Scrolling {clicks} ticks")

        if pyautogui:
            pyautogui.scroll(clicks)
        elif mouse_lib:
            mouse_lib.wheel(clicks)
        else:
            raise RuntimeError("No mouse backend available")

        return {"status": "success", "scrolled_ticks": clicks}

    def hover(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """Hovers the mouse over (x, y) for a given duration."""
        self.move_to(x, y, smooth=True)
        time.sleep(duration)
        return {"status": "success", "hovered_at": [x, y], "duration": duration}


mouse_controller = MouseController()
