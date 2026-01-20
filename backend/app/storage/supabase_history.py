"""
Supabase-backed chat message history for LangChain.
"""
from typing import List, Optional
try:
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
except Exception as e:
    print(f"[SupabaseHistory] Warning: LangChain import failed: {e}")
    BaseChatMessageHistory = object
    BaseMessage = object
    HumanMessage = object
    AIMessage = object
from app.core.database import supabase


class SupabaseChatMessageHistory(BaseChatMessageHistory):
    """
    Chat message history that stores messages in Supabase.
    """
    
    def __init__(self, conversation_id: str, user_id: str):
        self.conversation_id = conversation_id
        self.user_id = user_id
        
        # Ensure conversation exists
        try:
            # Check if conversation exists
            existing = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
            
            if not existing.data:
                # Create conversation
                supabase.table("conversations").insert({
                    "id": conversation_id,
                    "user_id": user_id,
                    "title": f"Conversation {conversation_id[:8]}"
                })
        except Exception as e:
            print(f"Error initializing conversation history: {e}")

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from Supabase."""
        try:
            response = supabase.table("messages") \
                .select("*") \
                .eq("conversation_id", self.conversation_id) \
                .execute()  # Note: API might not support order by in lightweight client easily, sorting in python
            
            # Sort by created_at
            stored_messages = sorted(response.data, key=lambda x: x.get('created_at', ''))
            
            messages = []
            for msg in stored_messages:
                content = msg.get("content", "")
                role = msg.get("role", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            
            return messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        try:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            
            supabase.table("messages").insert({
                "conversation_id": self.conversation_id,
                "role": role,
                "content": message.content
            })
            
            # Update conversation updated_at
            # Note: Lightweight client doesn't support PATCH easily yet, skipping for now
        except Exception as e:
            print(f"Error adding message: {e}")

    def clear(self) -> None:
        """Clear session memory from Supabase."""
        try:
            supabase.table("messages").eq("conversation_id", self.conversation_id).delete()
        except Exception as e:
            print(f"Error clearing history: {e}")
