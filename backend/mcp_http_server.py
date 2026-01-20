"""
MCP HTTP Wrapper Service
Runs MCP servers (Gmail, Calendar, Notion) and exposes them via HTTP endpoints.
This bypasses the async/stdio issues by using simple HTTP calls.
"""
import asyncio
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Global storage for MCP sessions
mcp_sessions: Dict[str, ClientSession] = {}

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}

class ToolCallResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


async def init_mcp_server(server_name: str, config: Dict[str, Any]):
    """Initialize a single MCP server connection."""
    try:
        server_params = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {})
        )
        
        # Create stdio connection
        read, write = await stdio_client(server_params).__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()
        
        mcp_sessions[server_name] = session
        print(f"[MCP HTTP] Initialized {server_name}")
        return True
    except Exception as e:
        print(f"[MCP HTTP] Failed to initialize {server_name}: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MCP servers on startup."""
    print("[MCP HTTP] Starting MCP HTTP Wrapper Service...")
    
    # Load config
    with open("mcp_config.json", "r") as f:
        config = json.load(f)
    
    # Initialize each server
    servers_to_init = ["gmail", "google-calendar", "notion"]
    for server_name in servers_to_init:
        if server_name in config.get("mcpServers", {}):
            await init_mcp_server(server_name, config["mcpServers"][server_name])
    
    print(f"[MCP HTTP] Ready! Initialized {len(mcp_sessions)} servers")
    yield
    
    # Cleanup on shutdown
    print("[MCP HTTP] Shutting down...")
    for session in mcp_sessions.values():
        try:
            await session.__aexit__(None, None, None)
        except:
            pass


app = FastAPI(title="MCP HTTP Wrapper", lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "servers": list(mcp_sessions.keys())
    }


@app.post("/{server_name}/call_tool")
async def call_tool(server_name: str, request: ToolCallRequest) -> ToolCallResponse:
    """
    Call a tool on the specified MCP server.
    
    Args:
        server_name: Name of MCP server (gmail, google-calendar, notion)
        request: Tool call request with tool_name and arguments
    """
    if server_name not in mcp_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Server '{server_name}' not initialized"
        )
    
    session = mcp_sessions[server_name]
    
    try:
        result = await session.call_tool(request.tool_name, arguments=request.arguments)
        return ToolCallResponse(
            success=True,
            result=result.model_dump() if hasattr(result, 'model_dump') else result
        )
    except Exception as e:
        return ToolCallResponse(
            success=False,
            result=None,
            error=str(e)
        )


@app.get("/{server_name}/list_tools")
async def list_tools(server_name: str):
    """List available tools for a server."""
    if server_name not in mcp_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Server '{server_name}' not initialized"
        )
    
    session = mcp_sessions[server_name]
    
    try:
        tools_result = await session.list_tools()
        tools = []
        for tool in tools_result.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
