"""
Direct Tool Executor - Uses native Python tool implementations instead of MCP SDK.
"""
from typing import Dict, Any, List
from app.tools import gmail_tools, calendar_tools, notion_tools


class DirectToolExecutor:
    """Executes tools directly without MCP."""
    
    def __init__(self):
        self.tool_modules = {
            'gmail': gmail_tools,
            'google-calendar': calendar_tools,
            'notion': notion_tools
        }
    
    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool directly.
        
        Args:
            server_name: Server name (gmail, google-calendar, notion)
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if server_name not in self.tool_modules:
            return {'success': False, 'error': f'Server {server_name} not found'}
        
        module = self.tool_modules[server_name]
        return module.execute_tool(tool_name, arguments)
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools for a server."""
        if server_name not in self.tool_modules:
            return []
        
        module = self.tool_modules[server_name]
        return module.list_tools()
    
    async def get_all_tools(self, server_names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Get all tools for requested servers."""
        all_tools = {}
        for server_name in server_names:
            all_tools[server_name] = await self.list_tools(server_name)
        return all_tools


# Global instance
direct_executor = DirectToolExecutor()
