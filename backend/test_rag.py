"""
Test RAG pipeline functionality.
"""
import asyncio
import os
import uuid
import httpx

async def test_rag():
    base_url = "http://localhost:8000/api"
    conversation_id = str(uuid.uuid4())
    print(f"Testing with Conversation ID: {conversation_id}")
    
    # 1. Use real text file
    filename = r"c:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
    
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found!")
        return

    print(f"\n1. Uploading document '{filename}'...")
    
    # 2. Upload Document
    # Use longer timeout for first-time model download/init
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(filename, "rb") as f:
            files = {"file": (os.path.basename(filename), f, "application/pdf")}
            data = {"conversation_id": conversation_id}
            
            response = await client.post(f"{base_url}/upload", files=files, data=data)
            
            print(f"Upload Status: {response.status_code}")
            print(f"Upload Response: {response.json()}")
            
    # 3. Chat with RAG
    print(f"\n2. Asking question about leaves...")
    chat_request = {
        "conversation_id": conversation_id,
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "message": "prpovide information regarding leaves",
        "web_search": False,
        "use_rag": True,
        "enabled_mcps": [],
        "enabled_tools": {}
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{base_url}/chat", json=chat_request)
        print(f"Chat Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Chat Response: {response.json()['message']}")
            if response.json().get('sources'):
                 print(f"Sources: {response.json()['sources']}")
        else:
            print(f"Chat Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_rag())
