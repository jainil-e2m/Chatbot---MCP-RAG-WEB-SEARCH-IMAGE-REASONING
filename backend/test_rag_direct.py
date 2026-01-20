"""
Simple direct test of RAG functions
"""
import uuid
from app.core.rag import process_document, create_vector_store, get_rag_context

# Test configuration
PDF_PATH = r"C:\Users\Jainil Trivedi\Desktop\n8n-docker\HRPolicy.pdf"
CONVERSATION_ID = str(uuid.uuid4())  # Use proper UUID

print("="*80)
print("DIRECT RAG TEST")
print("="*80)

# Step 1: Read and process PDF
print("\n[Step 1] Reading PDF...")
with open(PDF_PATH, 'rb') as f:
    content = f.read()
print(f"✓ Read {len(content)} bytes")

print("\n[Step 2] Extracting text...")
text = process_document(content, "HRPolicy.pdf")
print(f"✓ Extracted {len(text)} characters")
print(f"Preview: {text[:500]}...")

# Step 3: Create vector store
print("\n[Step 3] Creating vector store...")
success = create_vector_store(CONVERSATION_ID, text)
if success:
    print("✓ Vector store created")
else:
    print("✗ Vector store creation failed")
    exit(1)

# Step 4: Query
print("\n[Step 4] Querying...")
query = "Provide information regarding Leaves."
context = get_rag_context(CONVERSATION_ID, query)

if context:
    print(f"✓ Retrieved context ({len(context)} chars)")
    print("\n" + "="*80)
    print("CONTEXT:")
    print("="*80)
    print(context)
    print("="*80)
else:
    print("✗ No context retrieved")

print("\n✓ TEST COMPLETE")
