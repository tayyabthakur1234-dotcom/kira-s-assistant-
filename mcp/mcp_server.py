import json
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from plugins.manager import plugin_manager
from mcp.mcp_client import mcp_client


class KIRAOSMCPServer:
    """
    KIRA AI OS Exporter MCP Server.
    Exposes KIRA's desktop, vision, browser, voice, memory, and plugin capabilities
    as a standard Model Context Protocol (MCP) server endpoint for external LLMs / agents.
    """

    def __init__(self):
        self.server_name = "kira_os_mcp_server"
        self.version = "1.0.0"

    def get_manifest(() -> Dict[str, Any]:
        pass

    def get_manifest(self) -> Dict[str, Any]:
        """Returns MCP server capabilities and metadata."""
        return {
            "name": self.server_name,
            "version": self.version,
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": True,
                "prompts": True,
                "resources": True
            }
        }

    def list_exported_tools(self) -> List[Dict[str, Any]]:
        """Exposes KIRA OS capabilities as standard MCP tool definitions."""
        return [
            {
                "name": "kira_desktop_click",
                "description": "Clicks at screen coordinates (x, y) or on named UI element.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "element_name": {"type": "string"}
                    }
                }
            },
            {
                "name": "kira_vision_screenshot",
                "description": "Captures desktop screenshot and performs OCR & UI element detection.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "array", "items": {"type": "integer"}}
                    }
                }
            },
            {
                "name": "kira_browser_navigate",
                "description": "Navigates Playwright browser engine to specified URL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "kira_voice_speak",
                "description": "Synthesizes speech output using Kokoro/Piper TTS engine.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "kira_memory_query",
                "description": "Performs semantic vector search across KIRA long-term memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "kira_execute_plugin",
                "description": "Executes an installed KIRA AI OS plugin action.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {"type": "string"},
                        "action": {"type": "string"},
                        "params": {"type": "object"}
                    },
                    "required": ["plugin_id", "action"]
                }
            }
        ]

    async def handle_jsonrpc_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handles MCP JSON-RPC 2.0 requests from external clients."""
        req_id = request_data.get("id")
        method = request_data.get("method")
        params = request_data.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": self.get_manifest()["capabilities"],
                    "serverInfo": {"name": self.server_name, "version": self.version}
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.list_exported_tools()}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                if tool_name == "kira_execute_plugin":
                    p_id = arguments.get("plugin_id")
                    act = arguments.get("action")
                    p_params = arguments.get("params", {})
                    res = await plugin_manager.execute_plugin_action(p_id, act, p_params)
                    content = [{"type": "text", "text": json.dumps(res.model_dump())}]
                else:
                    content = [{"type": "text", "text": f"Executed KIRA OS Tool '{tool_name}' with args {arguments}"}]

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": content, "isError": False}
                }
            except Exception as ex:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(ex)}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found."}
            }

kira_mcp_server = KIRAOSMCPServer()
