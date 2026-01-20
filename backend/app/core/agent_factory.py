"""
Agent factory for creating LangChain conversation agents.
"""
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.tools import BaseTool
    from langchain_core.messages import HumanMessage, AIMessage
except Exception as e:
    print(f"[AgentFactory] Warning: LangChain import failed: {e}")
    # Define dummy classes to prevent ImportErrors in type hints
    ChatPromptTemplate = object
    MessagesPlaceholder = object
    BaseChatModel = object
    RunnableWithMessageHistory = object
    BaseChatMessageHistory = object
    BaseTool = object
    HumanMessage = object
    AIMessage = object

from typing import Optional, List, Union


def create_conversation_agent(
    llm: BaseChatModel,
    history: BaseChatMessageHistory,
    tools: Optional[List[BaseTool]] = None
):
    """
    Create a LangChain conversation chain with message history.
    
    Args:
        llm: Language model to use
        history: Chat message history
        tools: List of tools for agent to use
        
    Returns:
        Agent executor (if tools) or RunnableWithMessageHistory (if no tools)
    """
    
    if tools:
        # Create a tool-calling agent WITHOUT the history wrapper
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant with access to tools. Use them when needed to answer user questions."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Return executor directly - we'll manage history manually
        return executor
    else:
        # Simple chain with automatic history management
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Engage in natural conversation with the user."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        chain = prompt | llm

        # Wrap with message history
        chain_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
        return chain_with_history


async def run_agent(
    agent: Union[RunnableWithMessageHistory, object],
    message: str,
    session_id: str = "default",
    history: Optional[BaseChatMessageHistory] = None
) -> str:
    """
    Run the conversation chain with a user message.
    
    Args:
        agent: The conversation chain or AgentExecutor
        message: User message
        session_id: Session identifier
        history: Chat history (required for AgentExecutor)
        
    Returns:
        Agent response
    """
    # Check if this is an AgentExecutor (has tools attribute)
    if hasattr(agent, 'tools'):
        # AgentExecutor - manually manage history
        if not history:
            raise ValueError("History is required for AgentExecutor")
        
        # Get existing messages
        chat_history = history.messages
        
        # Use ainvoke for async execution
        response = await agent.ainvoke({
            "input": message,
            "chat_history": chat_history
        })
        
        # Extract output
        output = response.get("output", "I'm sorry, I couldn't process that.")
        
        # Manually add messages to history
        history.add_message(HumanMessage(content=message))
        history.add_message(AIMessage(content=output))
        
        return output
    else:
        # Simple chain with RunnableWithMessageHistory
        response = agent.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
        
        if hasattr(response, "content"):
            return response.content
        return str(response)
