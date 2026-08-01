import os
import subprocess
from typing import Dict, Any
from utils.logger import logger
from utils.security import security_guard

class PowerControls:
    """
    Windows OS Power Controls for sleep, lock, logout, hibernate,
    and security-guarded shutdown and system restart.
    """

    def lock_session(self) -> Dict[str, Any]:
        """Locks the Windows user workstation session."""
        logger.info("[PowerControls] Locking workstation session")
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return {"status": "success", "action": "lock"}
        return {"status": "simulated", "action": "lock"}

    def sleep_system(self) -> Dict[str, Any]:
        """Puts system into Sleep power mode."""
        logger.info("[PowerControls] Putting system to sleep")
        if os.name == 'nt':
            # SetSuspendState(0, 1, 0) -> Sleep
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return {"status": "success", "action": "sleep"}
        return {"status": "simulated", "action": "sleep"}

    def hibernate_system(self) -> Dict[str, Any]:
        """Puts system into Hibernate mode."""
        logger.info("[PowerControls] Hibernating system")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/h"])
            return {"status": "success", "action": "hibernate"}
        return {"status": "simulated", "action": "hibernate"}

    def logout_user(self) -> Dict[str, Any]:
        """Logs off the active user session."""
        logger.info("[PowerControls] Logging out user")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/l"])
            return {"status": "success", "action": "logout"}
        return {"status": "simulated", "action": "logout"}

    def restart_system(self, confirmed: bool = False, timeout_sec: int = 10) -> Dict[str, Any]:
        """
        Restarts the OS.
        REQUIRES CONFIRMATION.
        """
        security_guard.verify_action_confirmation(
            action="system_restart",
            confirmed=confirmed,
            details=f"System restart requested with {timeout_sec}s delay."
        )

        logger.warning(f"[PowerControls] System restart initiated in {timeout_sec} seconds")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/r", "/t", str(timeout_sec)])
            return {"status": "success", "action": "restart", "timeout_sec": timeout_sec}

        return {"status": "simulated", "action": "restart"}

    def shutdown_system(self, confirmed: bool = False, timeout_sec: int = 10) -> Dict[str, Any]:
        """
        Shuts down the OS completely.
        REQUIRES CONFIRMATION.
        """
        security_guard.verify_action_confirmation(
            action="system_shutdown",
            confirmed=confirmed,
            details=f"System shutdown requested with {timeout_sec}s delay."
        )

        logger.warning(f"[PowerControls] System shutdown initiated in {timeout_sec} seconds")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/s", "/t", str(timeout_sec)])
            return {"status": "success", "action": "shutdown", "timeout_sec": timeout_sec}

        return {"status": "simulated", "action": "shutdown"}


power_controls = PowerControls()
