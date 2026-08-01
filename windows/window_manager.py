import sys
from typing import List, Dict, Any, Optional, Union
from utils.logger import logger

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import win32gui
    import win32con
    import win32process
except ImportError:
    win32gui = None
    win32con = None
    win32process = None


class WindowManager:
    """
    Windows Native Window Manager to enumerate, focus, minimize, maximize,
    restore, move, resize, and close target application windows.
    """

    def enumerate_windows(self) -> List[Dict[str, Any]]:
        """Returns a list of all visible desktop top-level windows with handles and titles."""
        windows_list = []

        if sys.platform == "win32" and win32gui:
            def enum_cb(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title.strip():
                        rect = win32gui.GetWindowRect(hwnd)
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        result.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid,
                            "rect": {"left": rect[0], "top": rect[1], "right": rect[2], "bottom": rect[3]},
                            "width": rect[2] - rect[0],
                            "height": rect[3] - rect[1]
                        })

            win32gui.EnumWindows(enum_cb, windows_list)
        elif gw:
            for w in gw.getAllWindows():
                if w.title and w.title.strip():
                    windows_list.append({
                        "hwnd": getattr(w, "_hWnd", 0),
                        "title": w.title,
                        "pid": 0,
                        "rect": {"left": w.left, "top": w.top, "right": w.right, "bottom": w.bottom},
                        "width": w.width,
                        "height": w.height
                    })
        else:
            logger.warning("[WindowManager] Windows native libraries not available on non-Windows OS")

        return windows_list

    def find_windows(self, query: str) -> List[Dict[str, Any]]:
        """Finds windows matching title query substring (case-insensitive)."""
        all_wins = self.enumerate_windows()
        q = query.lower()
        return [w for w in all_wins if q in w["title"].lower()]

    def activate_window(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Activates / focuses window by HWND integer or window title substring."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found for identifier: {identifier}"}

        if sys.platform == "win32" and win32gui:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return {"status": "success", "activated_hwnd": hwnd}
            except Exception as e:
                logger.error(f"[WindowManager] Failed to activate window {hwnd}: {e}")
                return {"status": "error", "message": str(e)}

        return {"status": "simulated", "hwnd": hwnd}

    def minimize_window(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Minimizes specified window."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found for identifier: {identifier}"}

        if sys.platform == "win32" and win32gui:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return {"status": "success", "hwnd": hwnd, "action": "minimize"}

        return {"status": "simulated", "hwnd": hwnd}

    def maximize_window(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Maximizes specified window."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found for identifier: {identifier}"}

        if sys.platform == "win32" and win32gui:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return {"status": "success", "hwnd": hwnd, "action": "maximize"}

        return {"status": "simulated", "hwnd": hwnd}

    def restore_window(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Restores window from minimized or maximized state."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found for identifier: {identifier}"}

        if sys.platform == "win32" and win32gui:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return {"status": "success", "hwnd": hwnd, "action": "restore"}

        return {"status": "simulated", "hwnd": hwnd}

    def move_and_resize(self, identifier: Union[int, str], x: int, y: int, width: int, height: int) -> Dict[str, Any]:
        """Moves and resizes window to target bounding box (x, y, width, height)."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found: {identifier}"}

        if sys.platform == "win32" and win32gui:
            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return {"status": "success", "hwnd": hwnd, "new_bounds": [x, y, width, height]}

        return {"status": "simulated", "hwnd": hwnd, "bounds": [x, y, width, height]}

    def close_window(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Closes window cleanly by sending WM_CLOSE message."""
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found: {identifier}"}

        if sys.platform == "win32" and win32gui:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return {"status": "success", "hwnd": hwnd, "action": "close"}

        return {"status": "simulated", "hwnd": hwnd}

    def _resolve_hwnd(self, identifier: Union[int, str]) -> Optional[int]:
        if isinstance(identifier, int):
            return identifier
        matches = self.find_windows(str(identifier))
        if matches:
            return matches[0]["hwnd"]
        return None


window_manager = WindowManager()
