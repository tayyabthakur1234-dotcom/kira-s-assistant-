import subprocess
import sys
import time
from typing import Dict, Any, Optional
from utils.logger import logger

class CommandExecutor:
    """
    Subprocess execution manager supporting PowerShell, Windows CMD, and inline Python
    code execution with timeout guards, output capturing, and status codes.
    """

    def execute_powershell(self, script: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
        """Executes a PowerShell script string and returns stdout, stderr, and exit code."""
        logger.info(f"[CommandExecutor] Executing PowerShell command (timeout={timeout_sec}s)")
        cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]
        return self._run_subprocess(cmd, timeout_sec)

    def execute_cmd(self, command: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
        """Executes a CMD batch command and returns output."""
        logger.info(f"[CommandExecutor] Executing CMD command: {command}")
        cmd = ["cmd.exe", "/c", command] if os.name == 'nt' else ["sh", "-c", command]
        return self._run_subprocess(cmd, timeout_sec)

    def execute_python_code(self, code: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
        """Executes inline Python 3 code in an isolated subprocess and captures output."""
        logger.info("[CommandExecutor] Executing inline Python code payload")
        cmd = [sys.executable, "-c", code]
        return self._run_subprocess(cmd, timeout_sec)

    def _run_subprocess(self, cmd_args: list, timeout_sec: float) -> Dict[str, Any]:
        start_time = time.time()
        try:
            process = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                errors="replace"
            )
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "exit_code": process.returncode,
                "stdout": process.stdout.strip(),
                "stderr": process.stderr.strip(),
                "duration_ms": duration_ms
            }
        except subprocess.TimeoutExpired:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"[CommandExecutor] Command timed out after {timeout_sec}s")
            return {
                "status": "timeout",
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout_sec} seconds.",
                "duration_ms": duration_ms
            }
        except Exception as e:
            logger.error(f"[CommandExecutor] Execution failed: {e}")
            return {
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": round((time.time() - start_time) * 1000, 2)
            }


import os
command_executor = CommandExecutor()
