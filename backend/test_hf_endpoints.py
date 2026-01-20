"""
Test correct HuggingFace endpoint
"""
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    print("ERROR: HUGGINGFACE_API_KEY not found in environment variables!")
    exit(1)

print(f"API Key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")

# Try different endpoints
endpoints = [
    "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
]

headers = {"Authorization": f"Bearer {api_key}"}
payload = {"inputs": "This is a test"}

for url in endpoints:
    print(f"\n{'='*60}")
    print(f"Trying: {url}")
    print(f"{'='*60}")
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ SUCCESS!")
            print(f"  Response Type: {type(result)}")
            if isinstance(result, list):
                print(f"  Length: {len(result)}")
                if len(result) > 0:
                    print(f"  First element type: {type(result[0])}")
                    if isinstance(result[0], list):
                        print(f"  Embedding dimension: {len(result[0])}")
            print(f"  Full response: {json.dumps(result, indent=2)[:500]}")
            break
        else:
            print(f"✗ FAILED")
            print(f"  Response: {response.text}")
            
            # Check specific error messages
            try:
                error_json = response.json()
                print(f"  Parsed Error: {json.dumps(error_json, indent=2)}")
            except:
                pass
                
    except httpx.TimeoutException as e:
        print(f"✗ TIMEOUT: {e}")
    except httpx.RequestError as e:
        print(f"✗ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")

print(f"\n{'='*60}")
print("Test complete")