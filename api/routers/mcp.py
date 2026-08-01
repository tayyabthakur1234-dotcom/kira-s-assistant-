from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from mcp.mcp_registry import MCPServerConfig, MCPRunRequest, MCPRunResult
from mcp.mcp_client import mcp_client
from mcp.mcp_server import kira_mcp_server

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol"])


@router.post("/connect")
async def connect_mcp_server(req: MCPServerConfig):
    """Connects to an external MCP server, auto-authenticates, and discovers tools."""
    res = await mcp_client.connect_server(req)
    return res


@router.get("/tools")
@router.post("/tools")
def list_mcp_tools():
    """Lists all registered MCP tools discovered across connected MCP servers."""
    tools = mcp_client.list_tools()
    exported = kira_mcp_server.list_exported_tools()
    return {
        "status": "success",
        "discovered_mcp_tools": tools,
        "exported_kira_os_mcp_tools": exported
    }


@router.post("/run")
async def run_mcp_tool(req: MCPRunRequest):
    """Executes a tool call on a connected MCP server."""
    res = await mcp_client.run_tool(req)
    if res.status == "failed":
        raise HTTPException(status_code=400, detail=res.error)
    return res.model_dump()


@router.post("/jsonrpc")
async def mcp_jsonrpc_endpoint(request_body: Dict[str, Any]):
    """JSON-RPC 2.0 endpoint exposing KIRA AI OS as an MCP Server to external agents."""
    res = await kira_mcp_server.handle_jsonrpc_request(request_body)
    return res
