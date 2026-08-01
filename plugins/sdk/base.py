import time
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field


class PluginPermission(str, Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    NETWORK = "network"
    SYSTEM_EXEC = "system_exec"
    SEND_MESSAGES = "send_messages"
    PUBLISH_CODE = "publish_code"
    DELETE_CLOUD_FILES = "delete_cloud_files"
    MEDIA_CONTROL = "media_control"
    CALENDAR_ACCESS = "calendar_access"


class PluginManifest(BaseModel):
    id: str = Field(..., description="Unique plugin identifier string e.g. 'jira_github'")
    name: str = Field(..., description="Human readable plugin name")
    version: str = Field(default="1.0.0", description="SemVer plugin version")
    description: str = Field(..., description="Plugin functionality overview")
    author: str = Field(default="KIRA AI System")
    permissions: List[PluginPermission] = Field(default_factory=list)
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    category: str = Field(default="general")
    is_enabled: bool = Field(default=True)


class PluginContext(BaseModel):
    plugin_id: str
    config: Dict[str, Any] = Field(default_factory=dict)
    permissions_granted: List[PluginPermission] = Field(default_factory=list)


class PluginResult(BaseModel):
    status: str = Field(default="success", description="'success', 'failed', 'confirmation_required'")
    action: str = Field(..., description="Target action executed")
    data: Optional[Dict[str, Any]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    execution_time_ms: float = Field(default=0.0)


class BasePlugin:
    """
    Abstract Base Class for all KIRA AI OS Plugins.
    Provides standard lifecycle hooks, permission metadata, configuration handling,
    and action routing.
    """

    def __init__(self, manifest: PluginManifest, config: Optional[Dict[str, Any]] = None):
        self.manifest = manifest
        self.config = config or {}
        self.is_initialized = False

    def initialize(self) -> bool:
        """Lifecycle hook called when plugin is enabled or loaded."""
        self.is_initialized = True
        return True

    def shutdown(self) -> bool:
        """Lifecycle hook called when plugin is disabled or uninstalled."""
        self.is_initialized = False
        return True

    def get_info(self) -> Dict[str, Any]:
        """Returns plugin metadata info dict."""
        return {
            "manifest": self.manifest.model_dump(),
            "is_initialized": self.is_initialized
        }

    async def execute_action(self, action_name: str, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
        """
        Main execution router for plugin actions.
        Subclasses implement specific action methods.
        """
        start = time.time()
        method_name = f"action_{action_name}"
        method = getattr(self, method_name, None)

        if not method or not callable(method):
            return PluginResult(
                status="failed",
                action=action_name,
                error=f"Action '{action_name}' is not supported by plugin '{self.manifest.id}'.",
                execution_time_ms=round((time.time() - start) * 1000, 2)
            )

        try:
            res = await method(params=params, confirmed=confirmed)
            res.execution_time_ms = round((time.time() - start) * 1000, 2)
            return res
        except Exception as ex:
            return PluginResult(
                status="failed",
                action=action_name,
                error=str(ex),
                execution_time_ms=round((time.time() - start) * 1000, 2)
            )
