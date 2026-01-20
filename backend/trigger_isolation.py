"""
Trigger 500 Error (No RAG) - Isolation Test
"""
import requests
import uuid
import json

BASE_URL = "http://localhost:8000"
CONVERSATION_ID = "test-no-rag-isolation"

print("Triggering /api/chat WITHOUT RAG...")

payload = {
    "conversation_id": CONVERSATION_ID,
    "message": "Hi there",
    "model": "meta-llama/llama-3.3-70b-instruct",
    "use_rag": False,
    "web_search": False,
    "enabled_mcps": [],
    "enabled_tools": {},
    "user_id": "test-user-id"
}

try:
    response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
