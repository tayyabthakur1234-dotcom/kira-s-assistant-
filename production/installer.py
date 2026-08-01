"""
Installer Module - KIRA AI Operating System (Phase 12)
Manages dependency detection (Python, Git, Node, Rust, Playwright, PowerShell, VC++ Runtime),
silent/one-click installation scripts, installer build specs (MSI, EXE, Portable, Silent),
and Windows shortcuts / uninstaller registration.
"""

import os
import sys
import shutil
import subprocess
import platform
from typing import Dict, Any, List, Optional
from utils.logger import logger


class WindowsInstallerEngine:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.is_windows = platform.system().lower() == "windows"

    def detect_system_dependencies(self) -> Dict[str, Any]:
        """Detects presence and versions of system prerequisites."""
        deps = {
            "python": self._check_cli("python --version" if self.is_windows else "python3 --version"),
            "git": self._check_cli("git --version"),
            "node": self._check_cli("node --version"),
            "rust": self._check_cli("rustc --version"),
            "playwright": self._check_playwright(),
            "powershell": self._check_cli("powershell $PSVersionTable.PSVersion.ToString()"),
            "vcredist": self._check_vcredist() if self.is_windows else {"installed": True, "version": "N/A (Linux)"}
        }

        all_critical_installed = all([
            deps["python"]["installed"],
            deps["git"]["installed"],
            deps["node"]["installed"]
        ])

        return {
            "status": "success",
            "os": platform.system(),
            "architecture": platform.architecture()[0],
            "all_critical_installed": all_critical_installed,
            "dependencies": deps
        }

    def _check_cli(self, command: str) -> Dict[str, Any]:
        try:
            proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                output = (proc.stdout or proc.stderr).strip().splitlines()[0]
                return {"installed": True, "version": output}
            return {"installed": False, "version": None}
        except Exception:
            return {"installed": False, "version": None}

    def _check_playwright(self) -> Dict[str, Any]:
        try:
            proc = subprocess.run("npx playwright --version", shell=True, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                return {"installed": True, "version": proc.stdout.strip()}
            return {"installed": False, "version": None}
        except Exception:
            return {"installed": False, "version": None}

    def _check_vcredist(self) -> Dict[str, Any]:
        # Check VC++ Redistributable Registry keys or DLL presence
        system32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        vc_dll = os.path.join(system32, "vcruntime140.dll")
        if os.path.exists(vc_dll):
            return {"installed": True, "version": "VC++ 2015-2022 Runtime"}
        return {"installed": False, "version": None}

    def generate_installer_spec(self, target_type: str = "msi") -> Dict[str, Any]:
        """Generates configuration specifications for building Windows MSI/EXE/Portable installers."""
        target_type = target_type.lower()
        if target_type == "msi":
            return {
                "status": "success",
                "installer_type": "MSI Windows Installer",
                "output_filename": "KIRA_AI_OS_v1.0.0_Setup.msi",
                "configuration": {
                    "product_name": "KIRA AI Operating System",
                    "version": "1.0.0",
                    "publisher": "KIRA AI Enterprise",
                    "upgrade_code": "A8F2B1C9-D4E3-4F8A-9B2C-1D3E5F7A9B0C",
                    "create_desktop_shortcut": True,
                    "create_start_menu_shortcut": True,
                    "register_uninstaller": True,
                    "silent_installation_args": "/qn /norestart"
                }
            }
        elif target_type == "portable":
            return {
                "status": "success",
                "installer_type": "Portable Zip Executable",
                "output_filename": "KIRA_AI_OS_v1.0.0_Portable.zip",
                "configuration": {
                    "standalone_env": True,
                    "no_registry_footprint": True,
                    "bundled_python": True,
                    "bundled_node": True
                }
            }
        else:
            return {
                "status": "success",
                "installer_type": "EXE One-Click Installer",
                "output_filename": "KIRA_AI_OS_v1.0.0_Setup.exe",
                "configuration": {
                    "nsis_script": "installer/kira_setup.nsi",
                    "allow_custom_dir": True,
                    "silent_mode_flag": "/S"
                }
            }


installer_engine = WindowsInstallerEngine()
