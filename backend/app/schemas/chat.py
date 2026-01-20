"""
Chat schemas for request/response validation.
"""
from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class ChatRequest(BaseModel):
    """Chat request schema matching frontend expectations."""
    conversation_id: str
    model: str
    enabled_mcps: List[str]
    enabled_tools: Dict[str, List[str]]
    use_rag: bool
    web_search: bool = False  # Web search toggle
    image_generation: bool = False  # Image generation toggle
    message: str


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: str
    message: str
    sources: List[Dict[str, Any]] = []  # List of source objects with title, url, snippet
    images: List[str] = []
    image_url: Optional[str] = None  # Generated image URL
    tools_used: List[str] = []  # Tools that were used
