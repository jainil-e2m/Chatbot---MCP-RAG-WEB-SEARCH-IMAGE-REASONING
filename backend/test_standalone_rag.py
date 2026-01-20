"""
Standalone RAG test without app imports
"""
import os
import uuid
import httpx
from dotenv import load_dotenv
from io import BytesIO
from pypdf import PdfReader

load_dotenv()

# Configuration
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

print("="*80)
print("STANDALONE RAG TEST")
print("="*80)

# Step 1: Read PDF
print("\n[Step 1] Reading PDF...")
with open(PDF_PATH, 'rb') as f:
    content = f.read()
print(f"✓ Read {len(content)} bytes")

# Step 2: Extract text
print("\n[Step 2] Extracting text...")
pdf = PdfReader(BytesIO(content))
text = ""
for page in pdf.pages:
    text += page.extract_text() + "\n\n"
print(f"✓ Extracted {len(text)} characters")

# Step 3: Create chunks
print("\n[Step 3] Creating chunks...")
chunk_size = 3000
chunks = []
for i in range(0, len(text), chunk_size):
    chunk = text[i:i+chunk_size]
    if chunk.strip():
        chunks.append(chunk)

# Limit to 5 for testing
chunks = chunks[:5]
print(f"✓ Created {len(chunks)} chunks")

# Step 4: Generate embeddings
print("\n[Step 4] Generating embeddings...")
url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

embeddings = []
for i, chunk in enumerate(chunks):
    print(f"  Embedding chunk {i+1}/{len(chunks)}...")
    response = httpx.post(
        url,
        headers=headers,
        json={"inputs": chunk},
        timeout=30.0
    )
    
    if response.status_code == 200:
        embedding = response.json()
        # New API returns flat list of floats
        if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], float):
            embeddings.append(embedding)
        else:
            print(f"  ✗ Unexpected format: {type(embedding)}")
            break
    else:
        print(f"  ✗ Error: {response.status_code} - {response.text}")
        break

print(f"✓ Generated {len(embeddings)} embeddings ({len(embeddings[0]) if embeddings else 0} dims each)")

# Step 5: Store in Supabase
print("\n[Step 5] Storing in Supabase...")
conversation_id = str(uuid.uuid4())  # Use proper UUID
print(f"Conversation ID: {conversation_id}")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    data = {
        "conversation_id": conversation_id,
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

print("\n✓ TEST COMPLETE!")
print("="*80)
