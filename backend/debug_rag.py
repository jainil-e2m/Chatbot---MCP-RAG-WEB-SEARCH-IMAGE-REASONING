"""
Debug RAG Retrieval Quality
"""
import requests
import uuid
import sys
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
CONVERSATION_ID = str(uuid.uuid4())
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print("="*60)
print("RAG RETRIEVAL DEBUGGER")
print("="*60)
print(f"Conversation ID: {CONVERSATION_ID}")

# 1. Upload Document
print("\n[1] Uploading Document...")
try:
    with open(PDF_PATH, 'rb') as f:
        files = {'file': ('HRPolicy.pdf', f, 'application/pdf')}
        data = {'conversation_id': CONVERSATION_ID}
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            print("✓ Upload Successful")
            print(f"  Result: {response.json()}")
        else:
            print(f"✗ Upload Failed: {response.text}")
            sys.exit(1)
            
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 2. Inspect Vectors in Supabase (Count)
print("\n[2] Checking Database Vectors...")
try:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "count=exact"
    }
    
    # Check count of documents for this conversation
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/documents?conversation_id=eq.{CONVERSATION_ID}&select=count",
        headers=headers
    )
    # count is in Content-Range header usually, or just checking body
    print(f"  Status: {resp.status_code}")
    # Supabase often returns count in headers range
    content_range = resp.headers.get("content-range", "unknown")
    print(f"  Content-Range: {content_range}")
    
    # Also just fetch metadata
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/documents?conversation_id=eq.{CONVERSATION_ID}&select=metadata",
        headers=headers
    )
    if resp.status_code == 200:
        rows = resp.json()
        print(f"  Rows found: {len(rows)}")
    else:
        print(f"  Failed to fetch rows: {resp.text}")

except Exception as e:
    print(f"✗ Error checking DB: {e}")

# 3. Test Retrieval (Direct RPC Call)
print("\n[3] Testing Specific Query Retrieval...")
queries = ["leaves", "leave policy", "vacation"]

# Generate embedding manually
try:
    print("  Generating query embeddings...")
    for query in queries:
        print(f"\n  Query: '{query}'")
        emb_resp = httpx.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/text-embedding-3-small",
                "input": query
            },
            timeout=30.0
        )
        
        if emb_resp.status_code != 200:
            print(f"  ✗ Failed to embed query: {emb_resp.text}")
            continue
            
        query_embedding = emb_resp.json()["data"][0]["embedding"]
        
        # Call RPC
        rpc_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_documents",
            headers=headers,
            json={
                "query_embedding": query_embedding,
                "match_count": 3,
                "filter": {"conversation_id": CONVERSATION_ID}
            },
            timeout=30.0
        )
        
        if rpc_resp.status_code == 200:
            results = rpc_resp.json()
            print(f"    Found {len(results)} matches:")
            for i, res in enumerate(results):
                sim = res.get('similarity', 0)
                content = res.get('content', '')[:100].replace('\n', ' ')
                print(f"    {i+1}. [Sim: {sim:.4f}] {content}...")
                
                # Check for biological leaves content vs HR content
                if "photosynthesis" in content.lower():
                    print("    ⚠ ALERT: Found biological content!")
        else:
            print(f"    ✗ RPC Failed: {rpc_resp.text}")

except Exception as e:
    print(f"✗ Error testing retrieval: {e}")

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)
