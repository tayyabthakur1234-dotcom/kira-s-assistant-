import sys
import subprocess
from typing import Dict, Any, Optional
from utils.logger import logger

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    AudioUtilities = None

class SystemControls:
    """
    Windows System Controls manager for volume, mute state, display brightness,
    system clipboard, wallpaper configuration, and recycle bin management.
    """

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Sets master volume level (0 to 100)."""
        level = max(0, min(100, level))
        logger.info(f"[SystemControls] Setting volume to {level}%")

        if sys.platform == "win32" and AudioUtilities:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                # Convert 0-100 scalar
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return {"status": "success", "volume_level": level}
            except Exception as e:
                logger.error(f"[SystemControls] Pycaw volume control failed: {e}")

        # PowerShell fallback for Windows
        if sys.platform == "win32":
            ps_script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174) * {level // 2}"
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)

        return {"status": "success", "volume_level": level, "method": "fallback"}

    def change_volume(self, delta: int) -> Dict[str, Any]:
        """Increases or decreases volume by a given delta."""
        # Simple keypress emulation for quick volume up/down
        key = "volumeup" if delta > 0 else "volumedown"
        steps = abs(delta) // 2
        try:
            import pyautogui
            for _ in range(max(1, steps)):
                pyautogui.press(key)
            return {"status": "success", "delta": delta}
        except Exception:
            return {"status": "simulated", "delta": delta}

    def mute(self) -> Dict[str, Any]:
        """Mutes audio volume."""
        try:
            import pyautogui
            pyautogui.press("volumemute")
            return {"status": "success", "action": "mute"}
        except Exception:
            return {"status": "simulated", "action": "mute"}

    def unmute(self) -> Dict[str, Any]:
        """Unmutes audio volume."""
        return self.mute()  # Toggles mute

    def set_brightness(self, level: int) -> Dict[str, Any]:
        """Sets display brightness percentage (0-100)."""
        level = max(0, min(100, level))
        if sys.platform == "win32":
            ps_cmd = f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
            res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
            if res.returncode == 0:
                return {"status": "success", "brightness": level}
        return {"status": "simulated", "brightness": level}

    def get_clipboard(self) -> Dict[str, Any]:
        """Reads text from clipboard."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return {"status": "success", "clipboard_text": text}
        except Exception as e:
            return {"status": "error", "message": f"Clipboard empty or unreadable: {e}"}

    def set_clipboard(self, text: str) -> Dict[str, Any]:
        """Sets text content into clipboard."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return {"status": "success", "copied_length": len(text)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_wallpaper(self, image_path: str) -> Dict[str, Any]:
        """Sets desktop wallpaper image."""
        if sys.platform == "win32":
            import ctypes
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
            return {"status": "success", "wallpaper": image_path}
        return {"status": "simulated", "wallpaper": image_path}

    def empty_recycle_bin(self) -> Dict[str, Any]:
        """Clears Windows Recycle Bin."""
        if sys.platform == "win32":
            import ctypes
            SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
            # SHERB_NOCONFIRMATION = 0x00000001, SHERB_NOPROGRESSUI = 0x00000002, SHERB_NOSOUND = 0x00000004
            SHEmptyRecycleBin(None, None, 7)
            return {"status": "success", "action": "empty_recycle_bin"}
        return {"status": "simulated", "action": "empty_recycle_bin"}


system_controls = SystemControls()
