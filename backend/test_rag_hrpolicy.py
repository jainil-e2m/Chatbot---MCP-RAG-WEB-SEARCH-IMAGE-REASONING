"""
Test RAG system with HRPolicy.pdf using HuggingFace API embeddings
"""
import sys
import os
import requests

# Test configuration
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
BACKEND_URL = "http://localhost:8000"
CONVERSATION_ID = "test-hr-policy-rag-001"
QUERY = "Provide information regarding Leaves."

def test_upload():
    """Test document upload endpoint."""
    print("\n" + "="*80)
    print("STEP 1: UPLOADING DOCUMENT")
    print("="*80)
    
    try:
        with open(PDF_PATH, 'rb') as f:
            files = {'file': ('HRPolicy.pdf', f, 'application/pdf')}
            data = {'conversation_id': CONVERSATION_ID}
            
            print(f"Uploading: {PDF_PATH}")
            response = requests.post(
                f"{BACKEND_URL}/api/upload",
                files=files,
                data=data,
                timeout=300  # 5 minutes for embedding generation
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Upload successful!")
                print(f"  - Filename: {result.get('filename')}")
                print(f"  - Text length: {result.get('text_length')} characters")
                print(f"  - Conversation ID: {result.get('conversation_id')}")
                return True
            else:
                print(f"✗ Upload failed!")
                print(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"✗ Error during upload: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_query():
    """Test RAG query with uploaded document."""
    print("\n" + "="*80)
    print("STEP 2: QUERYING WITH RAG")
    print("="*80)
    
    try:
        payload = {
            "conversation_id": CONVERSATION_ID,
            "message": QUERY,
            "model": "meta-llama/llama-3.3-70b-instruct",
            "use_rag": True,
            "web_search": False,
            "enabled_mcps": [],
            "enabled_tools": {},
            "user_id": "test-user"
        }
        
        print(f"Query: {QUERY}")
        print(f"RAG enabled: True")
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Query successful!")
            print("\n" + "="*80)
            print("AI RESPONSE:")
            print("="*80)
            print(result.get('message', 'No response'))
            print("="*80)
            return True
        else:
            print(f"✗ Query failed!")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during query: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_without_rag():
    """Test same query without RAG for comparison."""
    print("\n" + "="*80)
    print("STEP 3: QUERYING WITHOUT RAG (for comparison)")
    print("="*80)
    
    try:
        payload = {
            "conversation_id": CONVERSATION_ID + "-no-rag",
            "message": QUERY,
            "model": "meta-llama/llama-3.3-70b-instruct",
            "use_rag": False,
            "web_search": False,
            "enabled_mcps": [],
            "enabled_tools": {},
            "user_id": "test-user"
        }
        
        print(f"Query: {QUERY}")
        print(f"RAG enabled: False")
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Query successful!")
            print("\n" + "="*80)
            print("AI RESPONSE (WITHOUT RAG):")
            print("="*80)
            print(result.get('message', 'No response'))
            print("="*80)
            return True
        else:
            print(f"✗ Query failed!")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RAG SYSTEM TEST - HR POLICY")
    print("="*80)
    print(f"PDF: {PDF_PATH}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Conversation ID: {CONVERSATION_ID}")
    print(f"Query: {QUERY}")
    
    # Check if PDF exists
    if not os.path.exists(PDF_PATH):
        print(f"\n✗ ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)
    
    # Check if backend is running
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"\n✗ ERROR: Backend not healthy")
            sys.exit(1)
        print(f"\n✓ Backend is healthy")
    except:
        print(f"\n✗ ERROR: Backend not reachable at {BACKEND_URL}")
        sys.exit(1)
    
    # Run tests
    upload_success = test_upload()
    
    if upload_success:
        rag_success = test_rag_query()
        test_without_rag()  # For comparison
        
        if rag_success:
            print("\n" + "="*80)
            print("✓ ALL TESTS PASSED!")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("✗ RAG QUERY FAILED")
            print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ UPLOAD FAILED - Cannot proceed with RAG test")
        print("="*80)
