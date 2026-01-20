"""
HTTP-based MCP executor - calls MCP wrapper service via REST.
"""
import httpx
from typing import List, Dict, Any


class HttpMcpExecutor:
    """Executes MCP tools via HTTP wrapper service."""
    
    def __init__(self, server_name: str, base_url: str = "http://127.0.0.1:8001"):
        self.server_name = server_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a single MCP tool via HTTP.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dict
            
        Returns:
            Tool execution result
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/{self.server_name}/call_tool",
                json={
                    "tool_name": tool_name,
                    "arguments": arguments
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return data.get("result")
            else:
                return {"error": data.get("error"), "tool": tool_name}
                
        except Exception as e:
            return {"error": str(e), "tool": tool_name}
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        try:
            response = await self.client.get(
                f"{self.base_url}/{self.server_name}/list_tools"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("tools", [])
        except Exception as e:
            print(f"[HttpMcpExecutor] Error listing tools: {e}")
            return []
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def create_http_executors(server_names: List[str]) -> Dict[str, HttpMcpExecutor]:
    """
    Create HTTP-based MCP executors.
    
    Args:
        server_names: List of MCP server names
        
    Returns:
        Dict mapping server name to HttpMcpExecutor
    """
    executors = {}
    
    for server_name in server_names:
        executors[server_name] = HttpMcpExecutor(server_name)
        print(f"[HttpMcpExecutor] Created executor for '{server_name}'")
    
    return executors


async def get_available_tools_http(
    executors: Dict[str, HttpMcpExecutor]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of available tools from all HTTP executors.
    
    Args:
        executors: Dict of HttpMcpExecutor instances
        
    Returns:
        Dict mapping server name to list of tool descriptions
    """
    all_tools = {}
    
    for server_name, executor in executors.items():
        tools = await executor.list_tools()
        all_tools[server_name] = tools
    
    return all_tools
