"""
Test RAG system with HRPolicy.pdf
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rag import process_document, create_vector_store, get_rag_context

def test_rag_pipeline():
    """Test the complete RAG pipeline."""
    
    # File path
    pdf_path = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
    conversation_id = "test-hr-policy-001"
    
    print("=" * 80)
    print("RAG SYSTEM TEST")
    print("=" * 80)
    
    # Step 1: Read PDF
    print("\n[Step 1] Reading PDF...")
    try:
        with open(pdf_path, 'rb') as f:
            file_content = f.read()
        print(f"✓ Read {len(file_content)} bytes from {pdf_path}")
    except Exception as e:
        print(f"✗ Failed to read PDF: {e}")
        return
    
    # Step 2: Extract text
    print("\n[Step 2] Extracting text with PyMuPDF + OCR...")
    try:
        text = process_document(file_content, "HRPolicy.pdf")
        print(f"✓ Extracted {len(text)} characters")
        print(f"  Preview: {text[:200]}...")
    except Exception as e:
        print(f"✗ Failed to extract text: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Create vector store
    print("\n[Step 3] Creating vector store (1024-dim embeddings, max 20 chunks)...")
    try:
        success = create_vector_store(conversation_id, text)
        if success:
            print("✓ Vector store created successfully")
        else:
            print("✗ Vector store creation failed")
            return
    except Exception as e:
        print(f"✗ Error creating vector store: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Query the vector store
    print("\n[Step 4] Querying: 'Provide information on the Leave Policy.'")
    try:
        query = "Provide information on the Leave Policy."
        context = get_rag_context(conversation_id, query, k=4)
        
        if context:
            print(f"✓ Retrieved {len(context)} characters of context")
            print("\n" + "=" * 80)
            print("RETRIEVED CONTEXT:")
            print("=" * 80)
            print(context)
            print("=" * 80)
        else:
            print("✗ No context retrieved")
    except Exception as e:
        print(f"✗ Error querying vector store: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_rag_pipeline()
