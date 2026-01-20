import asyncio
from contextlib import AsyncExitStack
from app.core.mcp_manager import McpManager
from app.core.model_router import get_llm
from app.core.agent_factory import create_conversation_agent, run_agent
from app.core.memory_manager import memory_manager

async def test_chat_with_mcp():
    print("Testing Chat with MCP...")
    
    try:
        # Get LLM
        llm = get_llm("meta-llama/llama-3.3-70b-instruct:free")
        print(f"✓ LLM loaded: {llm}")
        
        # Get history
        conversation_id = "test-conv-123"
        history = memory_manager.get_history(conversation_id)
        print(f"✓ History loaded for: {conversation_id}")
        
        # Load MCP tools
        async with AsyncExitStack() as stack:
            mcp_manager = McpManager.get_instance()
            print("Loading Gmail MCP...")
            tools = await mcp_manager.get_tools(["gmail"], stack)
            print(f"✓ Loaded {len(tools)} tools")
            
            # Create agent
            print("Creating agent...")
            agent = create_conversation_agent(llm=llm, history=history, tools=tools)
            print(f"✓ Agent created: {type(agent)}")
            
            # Run agent
            print("Running agent with test message...")
            response = run_agent(agent, "tell me my latest 2 emails", session_id=conversation_id)
            print(f"✓ Response: {response[:100]}...")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_with_mcp())
