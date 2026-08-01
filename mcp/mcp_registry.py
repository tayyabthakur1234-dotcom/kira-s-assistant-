from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    server_id: str = Field(..., description="Unique ID for the MCP server e.g. 'github_mcp'")
    name: str = Field(..., description="Display name of MCP server")
    transport: str = Field(default="http", description="'http', 'sse', or 'stdio'")
    endpoint: str = Field(..., description="Server URL or CLI command path")
    api_key: Optional[str] = Field(default=None, description="Auth token or API key if required")
    auto_connect: bool = Field(default=True)
    permissions_required: List[str] = Field(default_factory=list)


class MCPToolDef(BaseModel):
    server_id: str
    tool_name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)


class MCPRunRequest(BaseModel):
    server_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = Field(default=False)


class MCPRunResult(BaseModel):
    status: str = Field(default="success")
    server_id: str
    tool_name: str
    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    execution_time_ms: float = Field(default=0.0)
