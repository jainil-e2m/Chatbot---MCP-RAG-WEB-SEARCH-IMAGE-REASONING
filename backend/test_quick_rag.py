"""
Quick RAG test - Upload small document and query
"""
import requests
import uuid

BACKEND_URL = "http://localhost:8000"
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
CONVERSATION_ID = str(uuid.uuid4())
USER_ID = "00000000-0000-0000-0000-000000000000"

print("="*80)
print("QUICK RAG TEST")
print("="*80)
print(f"Conversation ID: {CONVERSATION_ID}")

# Upload document
print("\n[1] Uploading document...")
print("(This may take 1-2 minutes for embedding generation)")

try:
    with open(PDF_PATH, 'rb') as f:
        files = {'file': ('HRPolicy.pdf', f, 'application/pdf')}
        data = {'conversation_id': CONVERSATION_ID}
        
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            files=files,
            data=data,
            timeout=300  # 5 minutes
        )
        
        print(f"\nStatus: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Filename: {result.get('filename')}")
            print(f"  Text length: {result.get('text_length')} chars")
            print(f"  Conversation ID: {result.get('conversation_id')}")
        else:
            print(f"✗ Upload failed!")
            print(f"  Error: {response.text}")
            exit(1)
except requests.Timeout:
    print("\n✗ Upload timed out (embedding generation taking too long)")
    print("  This is normal for first-time use as HuggingFace API may be slow")
    print("  Checking if some chunks were stored...")
    # Continue to test query anyway
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Query with RAG
print("\n[2] Querying with RAG enabled...")
try:
    payload = {
        "conversation_id": CONVERSATION_ID,
        "message": "What is the leave policy?",
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
        print("AI RESPONSE:")
        print("="*80)
        print(result.get('message', 'No response'))
        print("="*80)
    else:
        print(f"\n✗ Query failed: {response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
