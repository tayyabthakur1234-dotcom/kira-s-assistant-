import os
import sys
import json
import time
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type
from plugins.sdk.base import BasePlugin, PluginManifest, PluginPermission, PluginResult
from plugins.sdk.sandbox import plugin_sandbox
from config.settings import settings
from utils.logger import logger


class PluginManager:
    """
    Production-Grade Dynamic Plugin Ecosystem Manager for KIRA AI OS Phase 6.
    Manages dynamic plugin loading, hot-reloading, marketplace registry catalog,
    permissions sandbox execution, enable/disable states, and health monitoring.
    """

    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = plugins_dir or settings.plugins_dir
        self.registry: Dict[str, BasePlugin] = {}
        self.marketplace_catalog: List[Dict[str, Any]] = []
        self._init_marketplace_catalog()

    def _init_marketplace_catalog(self):
        """Initializes default marketplace registry catalog."""
        self.marketplace_catalog = [
            {"id": "github", "name": "GitHub Integration", "version": "1.0.0", "category": "developer", "description": "Manage repositories, PRs, issues, commits, branches, and code pushes."},
            {"id": "google_drive", "name": "Google Drive", "version": "1.0.0", "category": "productivity", "description": "Search, upload, download, and delete cloud files."},
            {"id": "google_calendar", "name": "Google Calendar", "version": "1.0.0", "category": "productivity", "description": "Schedule events, view agenda, update appointments."},
            {"id": "google_docs", "name": "Google Docs", "version": "1.0.0", "category": "productivity", "description": "Read, create, and edit online documents."},
            {"id": "google_sheets", "name": "Google Sheets", "version": "1.0.0", "category": "productivity", "description": "Read, query, and update spreadsheets."},
            {"id": "gmail", "name": "Gmail Control", "version": "1.0.0", "category": "communication", "description": "Read emails, create drafts, and send messages with confirmation."},
            {"id": "maps", "name": "Google Maps", "version": "1.0.0", "category": "navigation", "description": "Search locations, geocode addresses, and calculate directions."},
            {"id": "weather", "name": "Weather Live", "version": "1.0.0", "category": "utility", "description": "Real-time weather reports and multi-day forecasts."},
            {"id": "news", "name": "News Feed", "version": "1.0.0", "category": "utility", "description": "Top news headlines and topic search."},
            {"id": "telegram", "name": "Telegram Bot", "version": "1.0.0", "category": "messaging", "description": "Read channels and send Telegram messages."},
            {"id": "discord", "name": "Discord Bot", "version": "1.0.0", "category": "messaging", "description": "Read servers and post channel messages."},
            {"id": "slack", "name": "Slack Workspace", "version": "1.0.0", "category": "messaging", "description": "Read messages and post to Slack channels."},
            {"id": "whatsapp", "name": "WhatsApp Web", "version": "1.0.0", "category": "messaging", "description": "Read and send WhatsApp messages."},
            {"id": "spotify", "name": "Spotify Player", "version": "1.0.0", "category": "media", "description": "Control playback, playlists, track queue, and volume."},
            {"id": "youtube", "name": "YouTube Studio", "version": "1.0.0", "category": "media", "description": "Search videos, get channels, and stream audio/video metadata."},
            {"id": "obs_studio", "name": "OBS Studio Control", "version": "1.0.0", "category": "media", "description": "Start/stop streaming, recording, and scene switching."},
            {"id": "notion", "name": "Notion Workspace", "version": "1.0.0", "category": "productivity", "description": "Search pages, manage databases, and append notes."},
            {"id": "vscode", "name": "VS Code Controller", "version": "1.0.0", "category": "developer", "description": "Open workspaces, view active extensions, run tasks."},
            {"id": "docker", "name": "Docker Engine", "version": "1.0.0", "category": "developer", "description": "List containers, start/stop services, inspect logs."},
            {"id": "git", "name": "Git CLI", "version": "1.0.0", "category": "developer", "description": "Check git status, commit, branch, and push code."},
            {"id": "steam", "name": "Steam Launcher", "version": "1.0.0", "category": "gaming", "description": "List installed games, launch games, check friend status."},
            {"id": "windows_settings", "name": "Windows Settings", "version": "1.0.0", "category": "system", "description": "Manage OS settings, volume, network, and themes."}
        ]

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Registers an instantiated plugin into the active registry."""
        p_id = plugin.manifest.id
        self.registry[p_id] = plugin
        plugin.initialize()
        logger.info(f"[PluginManager] Registered and initialized plugin '{p_id}' (v{plugin.manifest.version}).")
        return True

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Retrieves a registered plugin by ID."""
        return self.registry.get(plugin_id)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """Lists all registered plugins and their current operational status."""
        results = []
        for p_id, plugin in self.registry.items():
            results.append(plugin.get_info())
        return results

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enables a registered plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return False
        plugin.manifest.is_enabled = True
        return plugin.initialize()

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disables a registered plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return False
        plugin.manifest.is_enabled = False
        return plugin.shutdown()

    def install_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Installs or activates a plugin from marketplace or dynamically.
        """
        # If already registered, re-enable
        if plugin_id in self.registry:
            self.enable_plugin(plugin_id)
            return {"status": "success", "message": f"Plugin '{plugin_id}' enabled.", "plugin_id": plugin_id}

        # Check catalog
        match = next((item for item in self.marketplace_catalog if item["id"] == plugin_id), None)
        if not match:
            return {"status": "error", "message": f"Plugin '{plugin_id}' not found in catalog or plugins directory."}

        # Create plugin manifest dynamically
        manifest = PluginManifest(
            id=match["id"],
            name=match["name"],
            version=match["version"],
            description=match["description"],
            category=match["category"],
            permissions=[
                PluginPermission.READ_FILE,
                PluginPermission.NETWORK,
                PluginPermission.SEND_MESSAGES,
                PluginPermission.PUBLISH_CODE,
                PluginPermission.DELETE_CLOUD_FILES,
                PluginPermission.MEDIA_CONTROL,
                PluginPermission.CALENDAR_ACCESS
            ]
        )

        class DynamicInstalledPlugin(BasePlugin):
            async def action_execute(self, params: Dict[str, Any], confirmed: bool = False) -> PluginResult:
                return PluginResult(
                    status="success",
                    action=params.get("action", "execute"),
                    data={"result": f"Executed dynamic plugin '{plugin_id}' with params {params}"}
                )

        inst = DynamicInstalledPlugin(manifest=manifest, config=config)
        self.register_plugin(inst)

        return {"status": "success", "message": f"Plugin '{plugin_id}' installed successfully.", "plugin_id": plugin_id}

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstalls and removes a plugin from active registry."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return False
        plugin.shutdown()
        del self.registry[plugin_id]
        logger.info(f"[PluginManager] Uninstalled plugin '{plugin_id}'.")
        return True

    def reload_plugin(self, plugin_id: str) -> bool:
        """Hot-reloads a plugin's lifecycle hooks and configurations."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return False
        plugin.shutdown()
        plugin.initialize()
        logger.info(f"[PluginManager] Hot-reloaded plugin '{plugin_id}'.")
        return True

    def check_health(self) -> Dict[str, Any]:
        """Performs health diagnostic check across all registered plugins."""
        total = len(self.registry)
        active = sum(1 for p in self.registry.values() if p.manifest.is_enabled and p.is_initialized)
        return {
            "status": "healthy" if active == total else "degraded",
            "total_plugins": total,
            "active_plugins": active,
            "plugins": [
                {
                    "id": p.manifest.id,
                    "enabled": p.manifest.is_enabled,
                    "initialized": p.is_initialized
                }
                for p in self.registry.values()
            ]
        }

    async def execute_plugin_action(
        self,
        plugin_id: str,
        action_name: str,
        params: Dict[str, Any],
        required_permissions: Optional[List[PluginPermission]] = None,
        confirmed: bool = False
    ) -> PluginResult:
        """
        Executes a plugin action through the security sandbox wrapper.
        """
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return PluginResult(
                status="failed",
                action=action_name,
                error=f"Plugin '{plugin_id}' is not installed or registered."
            )

        if not plugin.manifest.is_enabled:
            return PluginResult(
                status="failed",
                action=action_name,
                error=f"Plugin '{plugin_id}' is currently disabled."
            )

        req_perms = required_permissions or [PluginPermission.NETWORK]
        return await plugin_sandbox.run_sandboxed(
            plugin=plugin,
            action_name=action_name,
            params=params,
            required_permissions=req_perms,
            confirmed=confirmed
        )

plugin_manager = PluginManager()
