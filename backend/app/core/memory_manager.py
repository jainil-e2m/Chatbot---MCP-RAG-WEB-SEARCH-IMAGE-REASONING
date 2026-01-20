"""
Memory manager for LangChain conversation memory with Supabase persistence.
"""
from typing import Dict
try:
    from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
    from langchain_core.messages import HumanMessage, AIMessage
    from app.storage.supabase_history import SupabaseChatMessageHistory
except Exception as e:
    print(f"[MemoryManager] Warning: Import failed: {e}")
    BaseChatMessageHistory = object
    InMemoryChatMessageHistory = object
    HumanMessage = object
    AIMessage = object
    SupabaseChatMessageHistory = object


class MemoryManager:
    """Manages conversation memory for different conversation IDs."""
    
    def __init__(self):
        # We don't cache history objects anymore since Supabase handles state
        # But we could cache the instance if needed
        self._histories: Dict[str, BaseChatMessageHistory] = {}
    
    def get_history(self, conversation_id: str) -> BaseChatMessageHistory:
        """
        Get chat message history for a conversation from Supabase.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            SupabaseChatMessageHistory instance
        """
        # For now, we're using a static user ID since auth context isn't fully passed here yet
        # In a real app, you'd pass the user_id from the request context
        # We'll use the conversation_id as a proxy or a default user for now
        # TODO: Pass authenticated user ID properly
        user_id = "default_user" 
        
        return SupabaseChatMessageHistory(
            conversation_id=conversation_id,
            user_id=user_id
        )
    
    def add_user_message(self, conversation_id: str, message: str):
        """Add a user message to the conversation history."""
        history = self.get_history(conversation_id)
        history.add_message(HumanMessage(content=message))
    
    def add_ai_message(self, conversation_id: str, message: str):
        """Add an AI message to the conversation history."""
        history = self.get_history(conversation_id)
        history.add_message(AIMessage(content=message))
    
    def clear_history(self, conversation_id: str):
        """Clear history for a specific conversation."""
        history = self.get_history(conversation_id)
        history.clear()
    
    def delete_history(self, conversation_id: str):
        """Delete history for a specific conversation."""
        self.clear_history(conversation_id)


# Global memory manager instance
memory_manager = MemoryManager()
