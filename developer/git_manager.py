"""
Git Manager Module - KIRA AI Operating System (Phase 10)
Provides automated Git operations: repository initialization, branch management,
commit creation with AI-generated messages, pulling, pushing, merging, and merge conflict resolution.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional
from utils.logger import logger
from router.model_router import model_router


class GitManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)

    def _run_git(self, args: List[str]) -> tuple[int, str, str]:
        cmd = ["git"] + args
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as e:
            return -1, "", str(e)

    def init_repo(self) -> Dict[str, Any]:
        """Initializes a Git repository in workspace root."""
        code, out, err = self._run_git(["init"])
        return {
            "status": "success" if code == 0 else "error",
            "output": out or err
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns git branch and file status."""
        code, out, err = self._run_git(["status", "--porcelain", "-b"])
        if code != 0:
            return {"status": "error", "message": err or "Failed to run git status"}

        lines = out.splitlines()
        branch = lines[0] if lines else "main"
        staged = []
        unstaged = []
        untracked = []

        for line in lines[1:]:
            if line.startswith("M ") or line.startswith("A "):
                staged.append(line[3:])
            elif line.startswith(" M") or line.startswith(" D"):
                unstaged.append(line[3:])
            elif line.startswith("??"):
                untracked.append(line[3:])

        return {
            "status": "success",
            "branch_raw": branch,
            "staged_count": len(staged),
            "unstaged_count": len(unstaged),
            "untracked_count": len(untracked),
            "files": {
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked
            }
        }

    async def commit_changes(
        self,
        message: Optional[str] = None,
        files: Optional[List[str]] = None,
        auto_generate_message: bool = True
    ) -> Dict[str, Any]:
        """Stages files and creates a git commit. Auto-generates AI commit message if requested."""
        if files:
            for f in files:
                self._run_git(["add", f])
        else:
            self._run_git(["add", "."])

        final_msg = message
        if not final_msg and auto_generate_message:
            # Generate smart commit message from git diff
            _, diff_out, _ = self._run_git(["diff", "--cached"])
            if not diff_out:
                _, diff_out, _ = self._run_git(["diff", "HEAD~1"])

            prompt = f"Generate a concise, professional Conventional Commit message (e.g. feat(core): add feature or fix(api): resolve bug) based on this git diff:\n\n{diff_out[:1500]}"
            res = await model_router.execute_with_failover(prompt=prompt, category="coding")
            final_msg = res.get("response", "feat(kira): update codebase with Developer Intelligence Engine").strip().replace('"', '')

        code, out, err = self._run_git(["commit", "-m", final_msg or "feat: automated commit by KIRA AI Engine"])
        return {
            "status": "success" if code == 0 else "error",
            "commit_message": final_msg,
            "output": out or err
        }

    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        code, out, err = self._run_git(["checkout", "-b", branch_name])
        return {"status": "success" if code == 0 else "error", "branch": branch_name, "output": out or err}

    def merge_branch(self, branch_name: str) -> Dict[str, Any]:
        code, out, err = self._run_git(["merge", branch_name])
        return {"status": "success" if code == 0 else "error", "merged_branch": branch_name, "output": out or err}


git_manager = GitManager()
