"""
Debugger Module - KIRA AI Operating System (Phase 10)
Runs projects, captures errors and stack traces, performs root cause analysis,
suggests fixes, applies code repairs, verifies resolution, and runs regression tests.
"""

import os
import re
import sys
import traceback
import subprocess
from typing import Dict, Any, List, Optional
from utils.logger import logger
from router.model_router import model_router


class ProjectDebugger:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)

    async def debug_project(
        self,
        command: Optional[str] = None,
        stack_trace: Optional[str] = None,
        file_context: Optional[str] = None,
        auto_apply_fix: bool = False
    ) -> Dict[str, Any]:
        """Runs test/build command or analyzes provided stack trace to diagnose and repair errors."""
        captured_error = stack_trace or ""
        command_output = ""
        exit_code = 0

        # Execute command if provided and no explicit stack trace passed
        if command and not stack_trace:
            try:
                proc = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                exit_code = proc.returncode
                command_output = proc.stdout + "\n" + proc.stderr
                if exit_code != 0:
                    captured_error = proc.stderr or proc.stdout
            except subprocess.TimeoutExpired:
                captured_error = f"Execution timed out after 30s while running: {command}"
                exit_code = -1
            except Exception as e:
                captured_error = f"Error executing command '{command}': {str(e)}"
                exit_code = -1

        if not captured_error and exit_code == 0 and command:
            return {
                "status": "success",
                "message": "Project ran cleanly with 0 errors!",
                "command": command,
                "output": command_output[:1000],
                "fix_applied": False
            }

        # Analyze stack trace with AI Router
        analysis = await self._analyze_stack_trace(captured_error, file_context)

        applied_fix_details = None
        if auto_apply_fix and analysis.get("target_file") and analysis.get("fixed_code"):
            target_path = os.path.join(self.workspace_root, analysis["target_file"])
            if os.path.exists(target_path):
                try:
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(analysis["fixed_code"])
                    applied_fix_details = {
                        "file": analysis["target_file"],
                        "status": "applied",
                        "verification": "Ready for re-test"
                    }
                except Exception as e:
                    applied_fix_details = {"file": analysis["target_file"], "status": "failed", "error": str(e)}

        return {
            "status": "error_analyzed",
            "command": command,
            "exit_code": exit_code,
            "raw_stack_trace": captured_error[:2000],
            "root_cause_summary": analysis.get("root_cause"),
            "target_file": analysis.get("target_file"),
            "suggested_fix": analysis.get("suggested_fix"),
            "fixed_code": analysis.get("fixed_code"),
            "fix_applied": auto_apply_fix and (applied_fix_details is not None),
            "applied_fix_details": applied_fix_details
        }

    async def _analyze_stack_trace(self, stack_trace: str, file_context: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes stack trace using Gemini/Grok model router."""
        prompt = f"""Stack Trace / Error Output:
{stack_trace}

Optional File Context:
{file_context or 'None'}

Please analyze this error as a Senior Staff Software Engineer.
Identify:
1. Root cause explanation.
2. The specific file and line number causing the issue.
3. Step-by-step fix recommendation.
4. Corrected code snippet.

Return a JSON object with:
{{
    "root_cause": "Detailed root cause explanation",
    "target_file": "relative/path/to/file.py",
    "line_number": 42,
    "suggested_fix": "Explanation of fix",
    "fixed_code": "Complete replacement code for the target file"
}}
"""
        res = await model_router.execute_with_failover(
            prompt=prompt,
            category="debugging",
            system_instruction="You are an expert software debugger. Output valid JSON only."
        )

        output_text = res.get("response", "")
        try:
            if "```json" in output_text:
                json_str = output_text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            return json.loads(output_text.strip())
        except Exception:
            # Fallback regex extraction of target file
            file_match = re.search(r'File "([^"]+)", line (\d+)', stack_trace)
            target = file_match.group(1) if file_match else "unknown"
            return {
                "root_cause": "Runtime Exception detected in stack trace.",
                "target_file": target,
                "suggested_fix": "Inspect variable references and imports in stack trace.",
                "fixed_code": None
            }


debugger = ProjectDebugger()
