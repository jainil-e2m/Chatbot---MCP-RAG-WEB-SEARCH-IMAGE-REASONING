"""
Direct MCP tool executor - bypasses LangChain agent complexity.
"""
import json
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpExecutor:
    """Executes MCP tools directly without LangChain wrapper."""
    
    def __init__(self, session: ClientSession, server_name: str):
        self.session = session
        self.server_name = server_name
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a single MCP tool.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dict
            
        Returns:
            Tool execution result
        """
        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            return {"error": str(e), "tool": tool_name}
    
    async def execute_plan(self, tool_calls: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple tool calls in sequence.
        
        Args:
            tool_calls: List of {"name": "tool_name", "args": {...}}
            
        Returns:
            List of results
        """
        results = []
        for call in tool_calls:
            tool_name = call.get("name")
            args = call.get("args", {})
            result = await self.execute_tool(tool_name, args)
            results.append({
                "tool": tool_name,
                "result": result
            })
        return results


async def create_mcp_executors(
    server_names: List[str],
    stack: AsyncExitStack,
    mcp_config: Dict[str, Any]
) -> Dict[str, McpExecutor]:
    """
    Create MCP executors for requested servers.
    
    Args:
        server_names: List of MCP server names to connect to
        stack: AsyncExitStack for managing connections
        mcp_config: MCP configuration dict
        
    Returns:
        Dict mapping server name to McpExecutor
    """
    executors = {}
    
    for server_name in server_names:
        if server_name not in mcp_config.get("mcpServers", {}):
            print(f"[McpExecutor] Server '{server_name}' not found in config")
            continue
        
        server_config = mcp_config["mcpServers"][server_name]
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config.get("args", []),
            env=server_config.get("env", {})
        )
        
        try:
            # Connect to server
            stdio_transport = await stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await stack.enter_async_context(ClientSession(stdio, write))
            
            # Initialize session
            await session.initialize()
            
            # Create executor
            executors[server_name] = McpExecutor(session, server_name)
            print(f"[McpExecutor] Connected to '{server_name}'")
            
        except Exception as e:
            print(f"[McpExecutor] Error connecting to '{server_name}': {e}")
    
    return executors


async def get_available_tools(
    executors: Dict[str, McpExecutor]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of available tools from all executors.
    
    Args:
        executors: Dict of McpExecutor instances
        
    Returns:
        Dict mapping server name to list of tool descriptions
    """
    all_tools = {}
    
    for server_name, executor in executors.items():
        try:
            # List tools from this server
            tools_result = await executor.session.list_tools()
            tools = []
            
            for tool in tools_result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            all_tools[server_name] = tools
            
        except Exception as e:
            print(f"[McpExecutor] Error listing tools from '{server_name}': {e}")
            all_tools[server_name] = []
    
    return all_tools
