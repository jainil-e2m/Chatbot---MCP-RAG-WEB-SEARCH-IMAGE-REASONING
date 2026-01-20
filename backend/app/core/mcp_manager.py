"""
MCP (Model Context Protocol) Manager.
Handles connections to local MCP servers via stdio and converts tools for LangChain.
"""
import asyncio
import json
import os
import shutil
from typing import Dict, List, Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import BaseTool, StructuredTool
from app.core.config import settings

class McpManager:
    _instance = None
    _config: Dict = {}
    _active_servers: Dict[str, Any] = {} # Map of server_name -> session/stack?
    
    # We might need to keep connections alive if they are expensive to spawn
    # But stdio connections are tied to the context manager scope.
    # For a persistent backend, we might need a background task loop or simpler per-request spawning.
    # Per-request spawning of 'npx' is SLOW (seconds).
    # We should likely maintain a global pool of connected sessions.
    
    def __init__(self):
        self.config_path = os.path.join(os.getcwd(), "mcp_config.json")
        self.load_config()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = McpManager()
        return cls._instance

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self._config = json.load(f)
        else:
            print(f"Warning: MCP config not found at {self.config_path}")

    async def get_tools(self, server_names: List[str], stack: AsyncExitStack) -> List[BaseTool]:
        """
        Connect to specified MCP servers and retrieve their tools.
        Uses AsyncExitStack to keep connections open during the request.
        """
        tools = []
        
        for name in server_names:
            params = self.get_server_params(name)
            if not params:
                print(f"[McpManager] Warning: Server '{name}' not found in config")
                continue
                
            try:
                # Start the server process (stdio)
                # This context manager keeps the process alive
                read_stream, write_stream = await stack.enter_async_context(stdio_client(params))
                
                # Create the session
                session = await stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                
                # Initialize
                await session.initialize()
                
                # List tools
                result = await session.list_tools()
                
                # Convert to LangChain tools
                for tool in result.tools:
                    # Check if tool is disabled in config
                    server_config = self._config.get("mcpServers", {}).get(name, {})
                    disabled_tools = server_config.get("disabledTools", [])
                    
                    if tool.name not in disabled_tools:
                        lc_tool = convert_mcp_tool_to_langchain(tool, session)
                        tools.append(lc_tool)
                        
                print(f"[McpManager] Connected to '{name}', loaded {len(result.tools)} tools")
                
            except Exception as e:
                print(f"[McpManager] Error connecting to '{name}': {e}")
                
        return tools

    def get_server_params(self, name: str) -> Optional[StdioServerParameters]:
        server_config = self._config.get("mcpServers", {}).get(name)
        if not server_config:
            return None
            
        return StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
            env={**os.environ, **server_config.get("env", {})}
        )

# Helper to bridge MCP Tool to LangChain
def convert_mcp_tool_to_langchain(mcp_tool, session) -> BaseTool:
    async def _run(
        *args, **kwargs
    ) -> str:
        # Construct arguments
        # LangChain creates simple args, MCP needs dict
        try:
            result = await session.call_tool(mcp_tool.name, arguments=kwargs)
            return str(result.content)
        except Exception as e:
            return f"Error executing tool {mcp_tool.name}: {str(e)}"

    return StructuredTool.from_function(
        func=None,
        coroutine=_run,
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        # We need to convert JSON schema to Pydantic or pass raw schema if supported
        # StructuredTool supportsargs_schema, but extracting it from JSON schema is complex dynamic pydantic.
        # Alternatively, we can assume LLM handles JSON args if we describe them well.
    )
