"""
Conversations API endpoints.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.conversation import Conversation, ConversationList
from app.storage.chat_history import chat_history_store

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationList)
async def get_conversations():
    """
    Get all conversations.
    
    Returns:
        List of all conversations with their messages
    """
    conversations = chat_history_store.get_all_conversations()
    return ConversationList(conversations=conversations)


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: Unique identifier for the conversation
        
    Returns:
        Conversation with all messages
    """
    try:
        conversation = chat_history_store.get_conversation(conversation_id)
        return conversation
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation not found: {str(e)}"
        )
