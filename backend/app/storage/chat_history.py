"""
In-memory chat history storage.
"""
from typing import Dict, List
from datetime import datetime
from app.schemas.conversation import Conversation, Message


class ChatHistoryStore:
    """In-memory storage for chat conversations."""
    
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
        self._conversation_images: Dict[str, List[Dict]] = {}  # Store images per conversation
    
    def get_conversation(self, conversation_id: str) -> Conversation:
        """Get or create a conversation."""
        if conversation_id not in self._conversations:
            now = datetime.utcnow()
            self._conversations[conversation_id] = Conversation(
                conversation_id=conversation_id,
                title=f"Conversation {conversation_id[:8]}",
                messages=[],
                created_at=now,
                updated_at=now
            )
        return self._conversations[conversation_id]
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to a conversation."""
        conversation = self.get_conversation(conversation_id)
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations."""
        return list(self._conversations.values())
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation."""
        conversation = self.get_conversation(conversation_id)
        return conversation.messages
    
    def add_image(self, conversation_id: str, image_base64: str, filename: str, image_format: str):
        """Add an image to a conversation."""
        if conversation_id not in self._conversation_images:
            self._conversation_images[conversation_id] = []
        
        self._conversation_images[conversation_id].append({
            'base64': image_base64,
            'filename': filename,
            'format': image_format,
            'uploaded_at': datetime.utcnow()
        })
        print(f"[ChatHistory] Added image {filename} to conversation {conversation_id}")
    
    def get_conversation_images(self, conversation_id: str) -> List[Dict]:
        """Get all images for a conversation."""
        return self._conversation_images.get(conversation_id, [])
    
    def has_images(self, conversation_id: str) -> bool:
        """Check if conversation has images."""
        return conversation_id in self._conversation_images and len(self._conversation_images[conversation_id]) > 0


# Global chat history store instance
chat_history_store = ChatHistoryStore()
