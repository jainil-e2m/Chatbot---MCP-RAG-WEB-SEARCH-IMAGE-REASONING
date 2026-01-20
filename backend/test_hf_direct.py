"""
Test HuggingFace API directly with httpx
"""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
print(f"API Key: {api_key}")
print(f"Length: {len(api_key)}")
print(f"Starts with 'hf_': {api_key.startswith('hf_')}")

# Test API call
url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {api_key}"}

print("\nTesting API call...")
response = httpx.post(
    url,
    headers=headers,
    json={"inputs": "This is a test"},
    timeout=30.0
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    embedding = response.json()
    print(f"\n✓ Success!")
    print(f"Embedding type: {type(embedding)}")
    print(f"Embedding length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
else:
    print(f"\n✗ Failed!")
