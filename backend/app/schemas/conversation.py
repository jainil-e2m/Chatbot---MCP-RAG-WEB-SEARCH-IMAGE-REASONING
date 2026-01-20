"""
Conversation schemas for request/response validation.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    """Individual message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class Conversation(BaseModel):
    """Conversation schema."""
    conversation_id: str
    title: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime


class ConversationList(BaseModel):
    """List of conversations."""
    conversations: List[Conversation]
