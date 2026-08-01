import os
import shutil
import glob
from typing import List, Dict, Any, Optional
from utils.logger import logger
from utils.security import security_guard

class FileExplorer:
    """
    File System Automation Manager for searching files, creating directories,
    copying, moving, renaming, opening, and securely deleting files.
    """

    def open_folder(self, folder_path: str) -> Dict[str, Any]:
        """Opens folder in Windows Explorer or returns directory contents."""
        if not os.path.exists(folder_path):
            return {"status": "error", "message": f"Path not found: {folder_path}"}

        if os.name == 'nt':
            os.startfile(folder_path)

        items = []
        for entry in os.scandir(folder_path):
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size_bytes": entry.stat().st_size if entry.is_file() else 0,
                "path": entry.path
            })

        return {"status": "success", "folder": folder_path, "items_count": len(items), "items": items[:100]}

    def create_folder(self, path: str) -> Dict[str, Any]:
        """Creates a new directory structure recursively."""
        try:
            os.makedirs(path, exist_ok=True)
            return {"status": "success", "created_path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def copy_item(self, src: str, dst: str) -> Dict[str, Any]:
        """Copies file or directory from src to dst."""
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            return {"status": "success", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def move_item(self, src: str, dst: str) -> Dict[str, Any]:
        """Moves or renames file or directory."""
        try:
            shutil.move(src, dst)
            return {"status": "success", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def rename_item(self, src: str, new_name: str) -> Dict[str, Any]:
        """Renames file or folder in its parent directory."""
        parent = os.path.dirname(src)
        dst = os.path.join(parent, new_name)
        return self.move_item(src, dst)

    def search_files(self, root_dir: str, pattern: str = "*") -> List[Dict[str, Any]]:
        """Searches for files matching pattern under target root directory."""
        results = []
        search_path = os.path.join(root_dir, "**", pattern)
        for filepath in glob.iglob(search_path, recursive=True):
            try:
                stat = os.stat(filepath)
                results.append({
                    "path": filepath,
                    "name": os.path.basename(filepath),
                    "size_bytes": stat.st_size,
                    "is_dir": os.path.isdir(filepath)
                })
                if len(results) >= 200:  # limit search safety
                    break
            except Exception:
                continue
        return results

    def delete_item(self, target_path: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Deletes a file or directory.
        REQUIRES CONFIRMATION SECURITY GUARD.
        """
        security_guard.verify_action_confirmation(
            action="file_delete",
            confirmed=confirmed,
            details=f"Permanent deletion of target path: '{target_path}'"
        )

        if not os.path.exists(target_path):
            return {"status": "error", "message": f"File or folder not found: {target_path}"}

        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            logger.info(f"[FileExplorer] Deleted target: {target_path}")
            return {"status": "success", "deleted_path": target_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}


file_explorer = FileExplorer()
