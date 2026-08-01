"""
VS Code Manager Module - KIRA AI Operating System (Phase 10)
Integrates with VS Code Extension API and workspace configs to open files, navigate symbols,
search codebase, manage terminal tasks, and generate launch.json/tasks.json configurations.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from utils.logger import logger


class VSCodeManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.vscode_dir = os.path.join(self.workspace_root, ".vscode")

    def generate_launch_and_tasks(self) -> Dict[str, Any]:
        """Generates launch.json and tasks.json in .vscode directory."""
        os.makedirs(self.vscode_dir, exist_ok=True)

        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "KIRA Python FastAPI Server",
                    "type": "python",
                    "request": "launch",
                    "module": "uvicorn",
                    "args": ["api.main:app", "--reload", "--port", "8000"],
                    "jinja": True
                },
                {
                    "name": "KIRA Express & Vite Server",
                    "type": "node",
                    "request": "launch",
                    "runtimeExecutable": "npm",
                    "runtimeArgs": ["run", "dev"],
                    "port": 3000
                }
            ]
        }

        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Run Pytest Suite",
                    "type": "shell",
                    "command": "pytest",
                    "args": ["-v"],
                    "group": {"kind": "test", "isDefault": True}
                },
                {
                    "label": "Build Application",
                    "type": "shell",
                    "command": "npm",
                    "args": ["run", "build"],
                    "group": {"kind": "build", "isDefault": True}
                }
            ]
        }

        launch_path = os.path.join(self.vscode_dir, "launch.json")
        tasks_path = os.path.join(self.vscode_dir, "tasks.json")

        with open(launch_path, 'w', encoding='utf-8') as f:
            json.dump(launch_config, f, indent=2)

        with open(tasks_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_config, f, indent=2)

        return {
            "status": "success",
            "vscode_dir": ".vscode",
            "files_created": ["launch.json", "tasks.json"]
        }

    def navigate_symbols(self, query: str) -> Dict[str, Any]:
        """Searches classes, functions, and symbols across workspace files."""
        matched_symbols = []
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'dist', 'build', '__pycache__')]
            for file in files:
                if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs', '.java')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.workspace_root)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f, start=1):
                                if re.search(r'(class|def|function|interface|type|const|let)\s+' + re.escape(query), line, re.IGNORECASE):
                                    matched_symbols.append({
                                        "file": rel_path,
                                        "line": idx,
                                        "symbol_declaration": line.strip()
                                    })
                    except Exception:
                        pass

        return {
            "status": "success",
            "query": query,
            "total_matches": len(matched_symbols),
            "symbols": matched_symbols[:30]
        }


vscode_manager = VSCodeManager()
