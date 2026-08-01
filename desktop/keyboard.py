import time
from typing import List, Union, Dict, Any, Optional
from utils.logger import logger

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import keyboard as keyboard_lib
except ImportError:
    keyboard_lib = None


class KeyboardController:
    """
    Modular Keyboard Engine for string typing, key presses, hotkeys,
    Windows shortcuts, and standard edit actions (copy/paste/undo/redo).
    """

    def type_text(self, text: str, interval: float = 0.02) -> Dict[str, Any]:
        """Types out a given string with an optional character delay."""
        logger.info(f"[KeyboardController] Typing string length {len(text)}")
        if pyautogui:
            pyautogui.write(text, interval=interval)
        elif keyboard_lib:
            keyboard_lib.write(text, delay=interval)
        else:
            raise RuntimeError("No keyboard automation backend available")

        return {"status": "success", "typed_length": len(text)}

    def press_key(self, key: str, presses: int = 1, interval: float = 0.05) -> Dict[str, Any]:
        """Presses a single key one or multiple times."""
        logger.info(f"[KeyboardController] Pressing key '{key}' x{presses}")
        if pyautogui:
            for _ in range(presses):
                pyautogui.press(key)
                time.sleep(interval)
        elif keyboard_lib:
            for _ in range(presses):
                keyboard_lib.send(key)
                time.sleep(interval)
        else:
            raise RuntimeError("No keyboard automation backend available")

        return {"status": "success", "key": key, "presses": presses}

    def execute_hotkey(self, keys: Union[List[str], str]) -> Dict[str, Any]:
        """
        Executes a key combo / hotkey sequence (e.g. ['ctrl', 'c'] or 'ctrl+alt+del').
        """
        if isinstance(keys, str):
            key_list = [k.strip() for k in keys.replace("+", " ").split()]
        else:
            key_list = keys

        logger.info(f"[KeyboardController] Executing hotkey: {key_list}")

        if pyautogui:
            pyautogui.hotkey(*key_list)
        elif keyboard_lib:
            keyboard_lib.send("+".join(key_list))
        else:
            raise RuntimeError("No keyboard backend available")

        return {"status": "success", "keys": key_list}

    # Standard Shortcuts
    def copy(self) -> Dict[str, Any]:
        """Executes Ctrl+C."""
        return self.execute_hotkey(["ctrl", "c"])

    def paste(self) -> Dict[str, Any]:
        """Executes Ctrl+V."""
        return self.execute_hotkey(["ctrl", "v"])

    def undo(self) -> Dict[str, Any]:
        """Executes Ctrl+Z."""
        return self.execute_hotkey(["ctrl", "z"])

    def redo(self) -> Dict[str, Any]:
        """Executes Ctrl+Y."""
        return self.execute_hotkey(["ctrl", "y"])

    def select_all(self) -> Dict[str, Any]:
        """Executes Ctrl+A."""
        return self.execute_hotkey(["ctrl", "a"])

    def win_key(self, additional_key: Optional[str] = None) -> Dict[str, Any]:
        """Presses Windows key alone or Win + key combo (e.g. Win+D for desktop)."""
        if additional_key:
            return self.execute_hotkey(["win", additional_key])
        return self.press_key("win")


keyboard_controller = KeyboardController()
