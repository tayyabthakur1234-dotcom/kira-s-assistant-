"""
Telemetry & Logging Engine - KIRA AI Operating System (Phase 12)
Provides structured JSON logging, performance metrics tracking, agent & plugin event stream,
execution history, and log archive exports.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from utils.logger import logger


class TelemetryLoggingEngine:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.audit_log_file = os.path.join(self.log_dir, "kira_audit.jsonl")

    def log_event(self, category: str, event_name: str, payload: Dict[str, Any], level: str = "INFO") -> None:
        """Logs a structured JSON event to the audit log."""
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,  # system, agent, plugin, security, dev
            "event": event_name,
            "level": level,
            "payload": payload
        }
        try:
            with open(self.audit_log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to write telemetry log: {e}")

    def get_recent_logs(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recent audit and execution logs."""
        logs = []
        if not os.path.exists(self.audit_log_file):
            return logs

        try:
            with open(self.audit_log_file, "r") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    if category and rec.get("category") != category:
                        continue
                    logs.append(rec)
                    if len(logs) >= limit:
                        break
        except Exception:
            pass
        return logs

    def export_logs_zip(self) -> Dict[str, Any]:
        """Packages all log files into an exportable zip."""
        export_path = os.path.join(self.log_dir, "kira_logs_export.json")
        logs = self.get_recent_logs(limit=200)
        with open(export_path, "w") as f:
            json.dump(logs, f, indent=2)
        return {
            "status": "success",
            "export_file": export_path,
            "total_records": len(logs)
        }


telemetry_engine = TelemetryLoggingEngine()
