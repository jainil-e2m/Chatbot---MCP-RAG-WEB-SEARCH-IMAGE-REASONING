"""
Trigger 500 Error and Analyze (Corrected Schema)
"""
import requests
import uuid
import json

BASE_URL = "http://localhost:8000"
CONVERSATION_ID = "test-500-debug"

print("Triggering /api/chat with RAG enabled...")

payload = {
    "conversation_id": CONVERSATION_ID,
    "message": "What is the specific leaves policy?",
    "model": "meta-llama/llama-3.3-70b-instruct",
    "use_rag": True,
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
