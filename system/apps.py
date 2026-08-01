import os
import subprocess
from typing import List, Dict, Any, Optional
import psutil
from utils.logger import logger

class AppManager:
    """
    Application Lifecycle Manager for detecting running tasks,
    launching executables, cleanly terminating processes, and restarting applications.
    """

    def detect_running_apps(self, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns a list of currently running processes with PID, name, CPU %, and memory info."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            try:
                pinfo = proc.info
                pname = pinfo.get('name', '') or ''
                if filter_name and filter_name.lower() not in pname.lower():
                    continue
                
                mem_mb = round((pinfo['memory_info'].rss / (1024 * 1024)), 2) if pinfo.get('memory_info') else 0
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pname,
                    "user": pinfo.get('username'),
                    "cpu_percent": pinfo.get('cpu_percent', 0.0),
                    "memory_mb": mem_mb
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def launch_app(self, app_path_or_cmd: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Launches an application by path or system executable command (e.g., 'notepad.exe', 'chrome.exe')."""
        try:
            cmd = [app_path_or_cmd] + (args if args else [])
            logger.info(f"[AppManager] Launching application command: {cmd}")
            proc = subprocess.Popen(cmd, shell=True if os.name == 'nt' else False)
            return {
                "status": "success",
                "launched_cmd": app_path_or_cmd,
                "pid": proc.pid
            }
        except Exception as e:
            logger.error(f"[AppManager] Failed to launch app '{app_path_or_cmd}': {e}")
            return {"status": "error", "message": str(e)}

    def close_app(self, identifier: Any, force: bool = False) -> Dict[str, Any]:
        """Closes application process by PID (int) or process name (str)."""
        closed_count = 0
        try:
            if isinstance(identifier, int):
                p = psutil.Process(identifier)
                if force:
                    p.kill()
                else:
                    p.terminate()
                closed_count = 1
            else:
                target_name = str(identifier).lower()
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target_name in (proc.info['name'] or '').lower():
                            if force:
                                proc.kill()
                            else:
                                proc.terminate()
                            closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            return {"status": "success", "closed_count": closed_count, "target": identifier}
        except Exception as e:
            logger.error(f"[AppManager] Failed to close app '{identifier}': {e}")
            return {"status": "error", "message": str(e)}

    def restart_app(self, app_path_or_cmd: str, identifier: Any) -> Dict[str, Any]:
        """Closes a running application and re-launches it."""
        close_res = self.close_app(identifier, force=True)
        launch_res = self.launch_app(app_path_or_cmd)
        return {
            "status": "success",
            "closed": close_res,
            "relaunched": launch_res
        }


app_manager = AppManager()
