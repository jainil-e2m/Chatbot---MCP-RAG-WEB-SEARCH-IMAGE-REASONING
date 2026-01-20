"""
Test OpenRouter embeddings directly
"""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key: {api_key[:15]}...")

url = "https://openrouter.ai/api/v1/embeddings"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "openai/text-embedding-3-small",
    "input": "This is a test sentence for embedding."
}

print("\nTesting OpenRouter embeddings...")
response = httpx.post(url, headers=headers, json=payload, timeout=30.0)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✓ Success!")
    print(f"  Response keys: {result.keys()}")
    if "data" in result:
        print(f"  Data length: {len(result['data'])}")
        if len(result['data']) > 0:
            embedding = result['data'][0]['embedding']
            print(f"  Embedding dims: {len(embedding)}")
            print(f"  First 5 values: {embedding[:5]}")
else:
    print(f"✗ Failed: {response.text}")
