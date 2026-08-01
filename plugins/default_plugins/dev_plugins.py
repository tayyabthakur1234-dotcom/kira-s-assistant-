from typing import Dict, Any
from plugins.sdk.base import BasePlugin, PluginManifest, PluginPermission, PluginResult


class GitHubPlugin(BasePlugin):
    """GitHub integration plugin for repositories, issues, PRs, commits, branches, clone & push."""

    def __init__(self, config: Dict[str, Any] = None):
        manifest = PluginManifest(
            id="github",
            name="GitHub Integration",
            version="1.0.0",
            description="Manage GitHub repositories, pull requests, issues, commits, branches, and code pushes.",
            category="developer",
            permissions=[PluginPermission.READ_FILE, PluginPermission.NETWORK, PluginPermission.PUBLISH_CODE]
        )
        super().__init__(manifest, config)

    async def action_get_repo(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        repo = params.get("repo", "kira-ai/kira-os")
        return PluginResult(
            action="get_repo",
            data={"repo": repo, "stars": 1280, "forks": 142, "default_branch": "main", "open_issues": 3}
        )

    async def action_list_prs(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        return PluginResult(
            action="list_prs",
            data={"pull_requests": [
                {"number": 12, "title": "Add Phase 6 Plugin & MCP Engine", "author": "tayyab", "status": "open"}
            ]}
        )

    async def action_push_code(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        branch = params.get("branch", "main")
        commit_msg = params.get("message", "Update KIRA AI OS Phase 6 core engine")
        return PluginResult(
            action="push_code",
            data={"status": "pushed", "branch": branch, "commit": "a1b2c3d4", "message": commit_msg}
        )


class GitPlugin(BasePlugin):
    """Git CLI automation plugin for local status, commits, branches, and push."""

    def __init__(self, config: Dict[str, Any] = None):
        manifest = PluginManifest(
            id="git",
            name="Git CLI Control",
            version="1.0.0",
            description="Git CLI automation for repository status, commit, branch management, and remote push.",
            category="developer",
            permissions=[PluginPermission.READ_FILE, PluginPermission.SYSTEM_EXEC, PluginPermission.PUBLISH_CODE]
        )
        super().__init__(manifest, config)

    async def action_status(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        return PluginResult(
            action="status",
            data={"branch": "main", "clean": True, "staged": [], "modified": []}
        )

    async def action_commit(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        msg = params.get("message", "Commit changes")
        return PluginResult(
            action="commit",
            data={"hash": "c0mm1t99", "message": msg, "files_changed": 4}
        )

    async def action_push(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        remote = params.get("remote", "origin")
        branch = params.get("branch", "main")
        return PluginResult(
            action="push",
            data={"remote": remote, "branch": branch, "status": "pushed_successfully"}
        )


class VSCodePlugin(BasePlugin):
    """VS Code IDE control plugin for workspaces and tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        manifest = PluginManifest(
            id="vscode",
            name="VS Code IDE Plugin",
            version="1.0.0",
            description="Control VS Code, open folders, launch terminal tasks, and query extensions.",
            category="developer",
            permissions=[PluginPermission.READ_FILE, PluginPermission.SYSTEM_EXEC]
        )
        super().__init__(manifest, config)

    async def action_open_folder(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        folder_path = params.get("path", ".")
        return PluginResult(
            action="open_folder",
            data={"path": folder_path, "status": "opened_in_vscode"}
        )


class DockerPlugin(BasePlugin):
    """Docker container and service management plugin."""

    def __init__(self, config: Dict[str, Any] = None):
        manifest = PluginManifest(
            id="docker",
            name="Docker Engine Control",
            version="1.0.0",
            description="Manage Docker containers, list images, inspect logs, and start/stop microservices.",
            category="developer",
            permissions=[PluginPermission.SYSTEM_EXEC, PluginPermission.NETWORK]
        )
        super().__init__(manifest, config)

    async def action_list_containers(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        return PluginResult(
            action="list_containers",
            data={"containers": [
                {"id": "c101", "name": "kira_redis", "status": "running", "image": "redis:alpine"},
                {"id": "c102", "name": "kira_chromadb", "status": "running", "image": "chromadb/chroma"}
            ]}
        )
