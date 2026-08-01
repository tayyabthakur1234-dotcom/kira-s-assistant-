import unittest
from fastapi.testclient import TestClient
from api.main import app
from plugins.sdk.base import BasePlugin, PluginManifest, PluginPermission, PluginResult
from plugins.sdk.sandbox import PluginSandbox, SecurityException
from plugins.manager import plugin_manager
from plugins.default_plugins import register_all_default_plugins
from mcp.mcp_registry import MCPServerConfig, MCPRunRequest
from mcp.mcp_client import mcp_client
from mcp.mcp_server import kira_mcp_server

client = TestClient(app)


class TestPluginsAndMCPEngine(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        register_all_default_plugins()

    def test_plugin_sdk_manifest_and_permissions(self):
        manifest = PluginManifest(
            id="test_plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Unit test plugin",
            permissions=[PluginPermission.READ_FILE, PluginPermission.SEND_MESSAGES]
        )
        assert manifest.id == "test_plugin"
        assert PluginPermission.SEND_MESSAGES in manifest.permissions

    async def test_sandbox_security_enforcement(self):
        class DummyPlugin(BasePlugin):
            async def action_send(self, params, confirmed=False):
                return PluginResult(action="send", data={"msg": "sent"})

        manifest = PluginManifest(
            id="dummy_m",
            name="Dummy Messaging",
            description="Test",
            permissions=[PluginPermission.SEND_MESSAGES]
        )
        p = DummyPlugin(manifest)
        sandbox = PluginSandbox(sandbox_enabled=True)

        # Unconfirmed execution should raise security confirmation requirement
        res_unconfirmed = await sandbox.run_sandboxed(
            plugin=p,
            action_name="send",
            params={},
            required_permissions=[PluginPermission.SEND_MESSAGES],
            confirmed=False
        )
        assert res_unconfirmed.status == "confirmation_required"

        # Confirmed execution should pass
        res_confirmed = await sandbox.run_sandboxed(
            plugin=p,
            action_name="send",
            params={},
            required_permissions=[PluginPermission.SEND_MESSAGES],
            confirmed=True
        )
        assert res_confirmed.status == "success"

    def test_plugin_manager_lifecycle(self):
        plugins = plugin_manager.list_plugins()
        assert len(plugins) >= 20

        # Check GitHub plugin is registered
        github_p = plugin_manager.get_plugin("github")
        assert github_p is not None
        assert github_p.manifest.name == "GitHub Integration"

        # Test disable & enable
        assert plugin_manager.disable_plugin("github") is True
        assert plugin_manager.get_plugin("github").manifest.is_enabled is False

        assert plugin_manager.enable_plugin("github") is True
        assert plugin_manager.get_plugin("github").manifest.is_enabled is True

        # Test health check
        health = plugin_manager.check_health()
        assert "status" in health
        assert health["total_plugins"] >= 20

    async def test_mcp_client_and_discovery(self):
        cfg = MCPServerConfig(
            server_id="brave_search",
            name="Brave Search",
            transport="http",
            endpoint="https://api.search.brave.com/mcp"
        )
        conn_res = await mcp_client.connect_server(cfg)
        assert conn_res["status"] == "connected"

        tools = mcp_client.list_tools()
        assert len(tools) > 0

        # Test MCP Tool Execution
        req = MCPRunRequest(
            server_id="brave_search",
            tool_name="brave_web_search",
            arguments={"query": "KIRA AI OS Phase 6"}
        )
        run_res = await mcp_client.run_tool(req)
        assert run_res.status == "success"
        assert run_res.output is not None

    async def test_mcp_server_exporter(self):
        manifest = kira_mcp_server.get_manifest()
        assert manifest["name"] == "kira_os_mcp_server"

        exported_tools = kira_mcp_server.list_exported_tools()
        assert len(exported_tools) >= 5

        # Handle JSON-RPC initialize
        init_res = await kira_mcp_server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize"
        })
        assert init_res["result"]["serverInfo"]["name"] == "kira_os_mcp_server"

        # Handle JSON-RPC tools/list
        tools_res = await kira_mcp_server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        })
        assert "tools" in tools_res["result"]

    def test_fastapi_plugins_and_mcp_endpoints(self):
        # /plugins/list
        resp_list = client.get("/plugins/list")
        assert resp_list.status_code == 200
        data = resp_list.json()
        assert data["status"] == "success"
        assert len(data["installed_plugins"]) >= 20

        # /plugins/execute (GitHub plugin get_repo)
        resp_exec = client.post("/plugins/execute", json={
            "plugin_id": "github",
            "action": "get_repo",
            "params": {"repo": "kira-ai/kira-os"},
            "confirmed": True
        })
        assert resp_exec.status_code == 200
        assert resp_exec.json()["status"] == "success"

        # /plugins/health
        resp_h = client.get("/plugins/health")
        assert resp_h.status_code == 200

        # /mcp/tools
        resp_mcp_tools = client.get("/mcp/tools")
        assert resp_mcp_tools.status_code == 200
        assert "discovered_mcp_tools" in resp_mcp_tools.json()

        # /mcp/jsonrpc
        resp_rpc = client.post("/mcp/jsonrpc", json={
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/list"
        })
        assert resp_rpc.status_code == 200
        assert resp_rpc.json()["id"] == 101


if __name__ == "__main__":
    unittest.main()
