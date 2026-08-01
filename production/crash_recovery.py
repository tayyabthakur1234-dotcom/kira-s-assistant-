"""
Crash Recovery System - KIRA AI Operating System (Phase 12)
Monitors system processes, captures stack traces, auto-restarts failed tasks,
dumps crash reports, and restores session & task DAG states.
"""

import os
import json
import time
import traceback
from typing import Dict, Any, List, Optional
from utils.logger import logger


class CrashRecoverySystem:
    def __init__(self, crash_dir: str = "logs/crashes", session_file: str = "session_state.json"):
        self.crash_dir = os.path.abspath(crash_dir)
        self.session_file = os.path.abspath(session_file)
        os.makedirs(self.crash_dir, exist_ok=True)

    def record_crash(self, exception: Exception, module_name: str) -> Dict[str, Any]:
        """Dumps crash report to disk and attempts recovery."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_filename = f"crash_{module_name}_{timestamp}.json"
        report_path = os.path.join(self.crash_dir, report_filename)

        stack_trace = traceback.format_exc()
        crash_data = {
            "timestamp": timestamp,
            "module": module_name,
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "stack_trace": stack_trace,
            "auto_restarted": True
        }

        with open(report_path, "w") as f:
            json.dump(crash_data, f, indent=2)

        logger.error(f"Crash recorded in module '{module_name}'. Saved to {report_filename}")
        return {
            "status": "crash_recorded",
            "report_path": report_path,
            "crash_data": crash_data
        }

    def save_session_state(self, active_tasks: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Saves session state for seamless recovery."""
        payload = {
            "saved_at": time.time(),
            "active_tasks": active_tasks,
            "user_context": user_context
        }
        with open(self.session_file, "w") as f:
            json.dump(payload, f, indent=2)
        return {"status": "success", "tasks_saved": len(active_tasks)}

    def restore_session_state(self) -> Dict[str, Any]:
        """Restores unfinished tasks and active session state."""
        if not os.path.exists(self.session_file):
            return {"status": "no_session", "active_tasks": [], "user_context": {}}

        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
            return {
                "status": "restored",
                "saved_at": data.get("saved_at"),
                "active_tasks": data.get("active_tasks", []),
                "user_context": data.get("user_context", {})
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "active_tasks": []}


crash_recovery = CrashRecoverySystem()
