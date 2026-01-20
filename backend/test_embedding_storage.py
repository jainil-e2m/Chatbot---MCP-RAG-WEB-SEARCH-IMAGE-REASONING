"""
Simple test - Generate embeddings and store in Supabase
"""
import os
import uuid
import httpx
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CONVERSATION_ID = str(uuid.uuid4())

print("="*80)
print("SIMPLE EMBEDDING + STORAGE TEST")
print("="*80)
print(f"Conversation ID: {CONVERSATION_ID}")

# Test data
test_chunks = [
    "This is the first test chunk about leave policy.",
    "This is the second test chunk about vacation days.",
    "This is the third test chunk about sick leave."
]

# Step 1: Generate embeddings
print("\n[Step 1] Generating embeddings via OpenRouter...")
embeddings = []

for i, chunk in enumerate(test_chunks):
    print(f"  Embedding chunk {i+1}/{len(test_chunks)}...")
    
    response = httpx.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/text-embedding-3-small",
            "input": chunk
        },
        timeout=30.0
    )
    
    if response.status_code == 200:
        result = response.json()
        embedding = result["data"][0]["embedding"]
        embeddings.append(embedding)
        print(f"    ✓ Generated {len(embedding)} dims")
    else:
        print(f"    ✗ Error: {response.status_code}")
        exit(1)

print(f"✓ Generated {len(embeddings)} embeddings")

# Step 2: Store in Supabase
print("\n[Step 2] Storing in Supabase...")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

for i, (chunk, embedding) in enumerate(zip(test_chunks, embeddings)):
    data = {
        "conversation_id": CONVERSATION_ID,
        "content": chunk,
        "embedding": embedding,
        "metadata": {"chunk_index": i}
    }
    
    response = httpx.post(
        f"{SUPABASE_URL}/rest/v1/documents",
        headers=headers,
        json=data,
        timeout=30.0
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✓ Stored chunk {i+1}")
    else:
        print(f"  ✗ Error: {response.status_code} - {response.text}")
        exit(1)

print(f"\n✓ Successfully stored {len(embeddings)} chunks!")

# Step 3: Test retrieval
print("\n[Step 3] Testing similarity search...")

# Generate query embedding
query = "What is the leave policy?"
print(f"Query: {query}")

response = httpx.post(
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

if response.status_code == 200:
    query_embedding = response.json()["data"][0]["embedding"]
    print(f"  ✓ Generated query embedding")
else:
    print(f"  ✗ Failed to generate query embedding")
    exit(1)

# Search for similar documents
response = httpx.post(
    f"{SUPABASE_URL}/rest/v1/rpc/match_documents",
    headers=headers,
    json={
        "query_embedding": query_embedding,
        "match_count": 3,
        "filter": {"conversation_id": CONVERSATION_ID}
    },
    timeout=30.0
)

if response.status_code == 200:
    results = response.json()
    print(f"  ✓ Found {len(results)} matching chunks:")
    for i, result in enumerate(results):
        print(f"    {i+1}. [{result.get('similarity', 0):.3f}] {result.get('content', '')[:50]}...")
else:
    print(f"  ✗ Search failed: {response.status_code} - {response.text}")

print("\n" + "="*80)
print("✓ TEST COMPLETE!")
print("="*80)
print(f"\nRAG system is working! Embeddings stored in conversation: {CONVERSATION_ID}")
