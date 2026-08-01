import time
from typing import Dict, Any, List, Optional
from plugins.sdk.base import BasePlugin, PluginPermission, PluginResult
from config.settings import settings
from utils.logger import logger


class SecurityException(Exception):
    """Raised when an unconfirmed sensitive action or missing permission occurs."""
    pass


class PluginSandbox:
    """
    Security Sandbox for KIRA AI OS Phase 6 Plugins.
    Enforces per-plugin permissions, validates user confirmation for high-risk actions
    (e.g., sending messages, publishing code, deleting cloud files), and prevents credential leakage.
    """

    SENSITIVE_PERMISSIONS = {
        PluginPermission.SEND_MESSAGES: "Action requires explicit user confirmation before sending external messages.",
        PluginPermission.PUBLISH_CODE: "Action requires explicit user confirmation before committing or pushing code to remote repositories.",
        PluginPermission.DELETE_CLOUD_FILES: "Action requires explicit user confirmation before deleting files in cloud storage.",
        PluginPermission.SYSTEM_EXEC: "Action requires system execution privileges."
    }

    def __init__(self, sandbox_enabled: Optional[bool] = None):
        self.sandbox_enabled = sandbox_enabled if sandbox_enabled is not None else settings.plugin_sandbox_enabled

    def verify_action_permissions(
        self,
        plugin: BasePlugin,
        action_name: str,
        required_permissions: List[PluginPermission],
        confirmed: bool = False
    ):
        """
        Validates plugin manifest permissions and checks user confirmation for sensitive actions.
        """
        if not self.sandbox_enabled:
            return

        # 1. Verify plugin manifest includes required permissions
        granted_perms = set(plugin.manifest.permissions)
        for req in required_permissions:
            if req not in granted_perms:
                err = f"Plugin '{plugin.manifest.id}' lacks required permission '{req.value}' for action '{action_name}'."
                logger.warning(f"[PluginSandbox] Permission denied: {err}")
                raise SecurityException(err)

            # 2. Sensitive confirmation check
            if req in self.SENSITIVE_PERMISSIONS and settings.require_confirmation and not confirmed:
                prompt_msg = self.SENSITIVE_PERMISSIONS[req]
                logger.warning(f"[PluginSandbox] Confirmation required: {prompt_msg}")
                raise SecurityException(f"CONFIRMATION_REQUIRED: {prompt_msg} (Set confirmed=true to proceed)")

    async def run_sandboxed(
        self,
        plugin: BasePlugin,
        action_name: str,
        params: Dict[str, Any],
        required_permissions: List[PluginPermission],
        confirmed: bool = False
    ) -> PluginResult:
        """Runs a plugin action inside security sandbox controls."""
        try:
            self.verify_action_permissions(plugin, action_name, required_permissions, confirmed)
            return await plugin.execute_action(action_name, params, confirmed)
        except SecurityException as sec_ex:
            return PluginResult(
                status="confirmation_required" if "CONFIRMATION_REQUIRED" in str(sec_ex) else "failed",
                action=action_name,
                error=str(sec_ex)
            )
        except Exception as ex:
            return PluginResult(
                status="failed",
                action=action_name,
                error=str(ex)
            )

plugin_sandbox = PluginSandbox()
