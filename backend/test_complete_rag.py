"""
Complete RAG test - Upload document and query with RAG
"""
import requests
import uuid

BACKEND_URL = "http://localhost:8000"
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
CONVERSATION_ID = str(uuid.uuid4())
USER_ID = "00000000-0000-0000-0000-000000000000"  # Nil UUID

print("="*80)
print("COMPLETE RAG TEST - Upload & Query")
print("="*80)
print(f"Conversation ID: {CONVERSATION_ID}")

# Step 1: Upload document
print("\n[Step 1] Uploading document...")
try:
    with open(PDF_PATH, 'rb') as f:
        files = {'file': ('HRPolicy.pdf', f, 'application/pdf')}
        data = {'conversation_id': CONVERSATION_ID}
        
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            files=files,
            data=data,
            timeout=180  # 3 minutes for embedding generation
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Filename: {result.get('filename')}")
            print(f"  Text length: {result.get('text_length')} chars")
        else:
            print(f"✗ Upload failed: {response.text}")
            exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Query with RAG enabled
print("\n[Step 2] Querying with RAG enabled...")
try:
    payload = {
        "conversation_id": CONVERSATION_ID,
        "message": "Provide information regarding Leaves.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "use_rag": True,
        "web_search": False,
        "enabled_mcps": [],
        "enabled_tools": {},
        "user_id": USER_ID
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json=payload,
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Query successful!")
        print("\n" + "="*80)
        print("AI RESPONSE (WITH RAG):")
        print("="*80)
        print(result.get('message', 'No response'))
        print("="*80)
    else:
        print(f"✗ Query failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Query WITHOUT RAG for comparison
print("\n[Step 3] Querying WITHOUT RAG for comparison...")
try:
    payload = {
        "conversation_id": str(uuid.uuid4()),  # Different conversation
        "message": "Provide information regarding Leaves.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "use_rag": False,
        "web_search": False,
        "enabled_mcps": [],
        "enabled_tools": {},
        "user_id": USER_ID
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json=payload,
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Query successful!")
        print("\n" + "="*80)
        print("AI RESPONSE (WITHOUT RAG):")
        print("="*80)
        print(result.get('message', 'No response'))
        print("="*80)
    else:
        print(f"✗ Query failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
print("✓ RAG TEST COMPLETE!")
print("="*80)
print("\nCompare the two responses above:")
print("- WITH RAG: Should provide specific information from HRPolicy.pdf")
print("- WITHOUT RAG: Should give generic information about leaves")
