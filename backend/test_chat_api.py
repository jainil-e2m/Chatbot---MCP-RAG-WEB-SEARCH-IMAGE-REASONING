import requests
import json

url = "http://localhost:8000/api/chat"
payload = {
    "conversation_id": "test-debug-123",
    "message": "tell me my latest 2 emails",
    "model": "meta-llama/llama-3.3-70b-instruct:free",
    "enabled_mcps": ["gmail"],
    "enabled_tools": {"gmail": ["search_emails", "read_email"]},
    "web_search": False,
    "use_rag": False
}

print("Sending chat request...")
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
