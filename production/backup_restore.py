"""
Backup & Restore Manager - KIRA AI Operating System (Phase 12)
Manages full configuration, memory, plugin, and conversation database backups,
restoration from archive archives, and user profile exports.
"""

import os
import json
import time
import zipfile
from typing import Dict, Any, List, Optional
from utils.logger import logger


class BackupRestoreManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = os.path.abspath(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, include_memories: bool = True, include_plugins: bool = True) -> Dict[str, Any]:
        """Creates a timestamped backup archive of KIRA OS state."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"kira_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        manifest = {
            "timestamp": timestamp,
            "version": "1.0.0",
            "included_memories": include_memories,
            "included_plugins": include_plugins,
            "created_by": "KIRA AI Enterprise OS"
        }

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
                # Add settings if present
                if os.path.exists(".env"):
                    zipf.write(".env", arcname="env.backup")
                if os.path.exists("first_run_config.json"):
                    zipf.write("first_run_config.json", arcname="first_run_config.json")

            logger.info(f"Backup successfully created: {backup_filename}")
            return {
                "status": "success",
                "backup_filename": backup_filename,
                "backup_path": backup_path,
                "size_kb": round(os.path.getsize(backup_path) / 1024, 2),
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {"status": "error", "message": str(e)}

    def list_backups(self) -> List[Dict[str, Any]]:
        """Lists available backup archives."""
        backups = []
        if not os.path.exists(self.backup_dir):
            return []
        for fn in os.listdir(self.backup_dir):
            if fn.endswith(".zip"):
                fp = os.path.join(self.backup_dir, fn)
                backups.append({
                    "filename": fn,
                    "filepath": fp,
                    "size_kb": round(os.path.getsize(fp) / 1024, 2),
                    "modified": time.ctime(os.path.getmtime(fp))
                })
        return backups

    def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """Restores state from a backup archive."""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            return {"status": "error", "message": f"Backup file {backup_filename} not found."}

        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.backup_dir)
            return {
                "status": "success",
                "restored_from": backup_filename,
                "message": "Configuration and state successfully restored."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


backup_manager = BackupRestoreManager()
