"""
Enhanced RAG implementation with pypdf and HuggingFace API embeddings.
No local ML dependencies or DLLs required.
"""
import os
from typing import List, Optional
from datetime import datetime
from io import BytesIO
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

# Global singleton for embedding model
_embedding_model = None

# Custom embedding class using OpenAI API via OpenRouter
class OpenRouterEmbeddings:
    """Direct HTTP calls to OpenRouter for OpenAI embeddings."""
    
    def __init__(self, api_key: str, model: str = "openai/text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/embeddings"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        embeddings = []
        for text in texts:
            response = httpx.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                # OpenAI format: {data: [{embedding: [...]}]}
                if "data" in result and len(result["data"]) > 0:
                    embedding = result["data"][0]["embedding"]
                    embeddings.append(embedding)
                else:
                    raise ValueError(f"Unexpected response format: {result}")
            else:
                raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embed_documents([text])[0]


def get_embedding_model():
    """
    Get or create the singleton embedding model.
    Uses OpenAI embeddings via OpenRouter (text-embedding-3-small, 1536 dims).
    """
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
        
    print("[RAG] Initializing OpenAI embeddings via OpenRouter...")
    try:
        # Get API key from settings
        api_key = settings.openrouter_api_key
        if not api_key:
            print("[RAG] ERROR: OPENROUTER_API_KEY not configured in settings")
            return None
        
        print(f"[RAG] Using OpenRouter API key: {api_key[:10]}...")
        
        # Use custom implementation
        _embedding_model = OpenRouterEmbeddings(
            api_key=api_key,
            model="openai/text-embedding-3-small"
        )
        print(f"[RAG] Loaded OpenAI embeddings via OpenRouter (1536 dims)")
        return _embedding_model
    except Exception as e:
        print(f"[RAG] Failed to load embeddings: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_document(file_content: bytes, filename: str) -> str:
    """
    Extract text from a document using pypdf.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Extracted text
    """
    if filename.lower().endswith('.pdf'):
        try:
            # Open PDF with pypdf
            pdf = PdfReader(BytesIO(file_content))
            text = ""
            
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
                
                if page_num % 10 == 0:
                    print(f"[RAG] Processed page {page_num + 1}/{len(pdf.pages)}")
            
            print(f"[RAG] Extracted {len(text)} characters from {len(pdf.pages)} pages")
            return text
            
        except Exception as e:
            print(f"[RAG] Error processing PDF: {e}")
            return ""
    else:
        # Plain text file
        try:
            return file_content.decode('utf-8')
        except:
            return file_content.decode('latin-1')


def create_vector_store(conversation_id: str, text: str) -> bool:
    """
    Create/Update Supabase vector store for a conversation.
    Limits to maximum 20 chunks.
    Uses direct REST API to avoid dependency issues.
    
    Args:
        conversation_id: Conversation ID
        text: Document text
        
    Returns:
        Success status
    """
    embeddings_model = get_embedding_model()
    if not embeddings_model:
        print("[RAG] Embedding model not available")
        return False
        
    try:
        # Split text into chunks (3000 chars with 600 overlap)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=600,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            print("[RAG] No chunks created from text")
            return False
        
        # Limit to 20 chunks
        if len(chunks) > 20:
            print(f"[RAG] Limiting from {len(chunks)} to 20 chunks")
            # Take evenly distributed chunks
            step = len(chunks) / 20
            chunks = [chunks[int(i * step)] for i in range(20)]
        
        print(f"[RAG] Processing {len(chunks)} chunks for conversation {conversation_id}")
        
        # Generate embeddings via HuggingFace API
        print("[RAG] Generating embeddings via HuggingFace API...")
        embeddings_list = embeddings_model.embed_documents(chunks)
        
        # Use httpx for direct REST API calls
        import httpx
        
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Insert chunks with embeddings
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
            data = {
                "conversation_id": conversation_id,
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "chunk_index": i,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            response = httpx.post(
                f"{settings.supabase_url}/rest/v1/documents",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                print(f"[RAG] Error inserting chunk {i}: {response.status_code} - {response.text}")
                return False
        
        print(f"[RAG] Successfully stored {len(chunks)} chunks")
        return True
        
    except Exception as e:
        print(f"[RAG] Error creating vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_rag_context(conversation_id: str, query: str, k: int = 4) -> str:
    """
    Retrieve context from Supabase Vector Store using similarity search.
    Uses direct REST API calls.
    
    Args:
        conversation_id: Conversation ID
        query: Search query
        k: Number of chunks to retrieve
        
    Returns:
        Retrieved context
    """
    embeddings_model = get_embedding_model()
    if not embeddings_model:
        return ""
        
    try:
        # Generate query embedding via HuggingFace API
        query_embedding = embeddings_model.embed_query(query)
        
        # Use httpx for direct RPC call
        import httpx
        
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Call match_documents RPC function
        response = httpx.post(
            f"{settings.supabase_url}/rest/v1/rpc/match_documents",
            headers=headers,
            json={
                'query_embedding': query_embedding,
                'match_count': k,
                'filter': {'conversation_id': conversation_id}
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            print(f"[RAG] Error querying documents: {response.status_code} - {response.text}")
            return ""
        
        result_data = response.json()
        
        if not result_data:
            print(f"[RAG] No documents found for conversation {conversation_id}")
            return ""
        
        # Combine retrieved chunks
        print(f"[RAG] Found {len(result_data)} chunks:")
        for i, doc in enumerate(result_data):
            score = doc.get('similarity', 0)
            content_preview = doc['content'][:100].replace('\n', ' ')
            print(f"[RAG] Chunk {i+1} (Score: {score:.4f}): {content_preview}...")
            
        context = "\n\n".join([doc['content'] for doc in result_data])
        print(f"[RAG] Retrieved {len(result_data)} chunks ({len(context)} chars)")
        
        return context
        
    except Exception as e:
        print(f"[RAG] Error retrieving context: {e}")
        import traceback
        traceback.print_exc()
        return ""


def clear_vector_store(conversation_id: str) -> bool:
    """
    Clear all documents for a conversation.
    Uses direct REST API calls.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Success status
    """
    try:
        import httpx
        
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json"
        }
        
        response = httpx.delete(
            f"{settings.supabase_url}/rest/v1/documents?conversation_id=eq.{conversation_id}",
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code in [200, 204]:
            print(f"[RAG] Cleared documents for conversation {conversation_id}")
            return True
        else:
            print(f"[RAG] Error clearing documents: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[RAG] Error clearing vector store: {e}")
        return False
