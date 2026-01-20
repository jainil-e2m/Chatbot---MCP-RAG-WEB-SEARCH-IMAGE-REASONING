
import asyncio
import os
from contextlib import AsyncExitStack
from app.core.mcp_manager import McpManager

# Mock settings just in case
os.environ["GOOGLE_OAUTH_CREDENTIALS"] = r"C:\Users\Jainil Trivedi\.calendar-mcp\gcp-oauth.keys.json"

async def test_mcp_connection():
    print("Testing MCP Connection for 'gmail'...")
    manager = McpManager.get_instance()
    
    async with AsyncExitStack() as stack:
        try:
            print("Attempting to load tools...")
            tools = await manager.get_tools(["gmail"], stack)
            print(f"Success! Loaded {len(tools)} tools.")
            for tool in tools:
                print(f" - {tool.name}: {tool.description[:50]}...")
                
            return True
        except Exception as e:
            print(f"MCP Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
