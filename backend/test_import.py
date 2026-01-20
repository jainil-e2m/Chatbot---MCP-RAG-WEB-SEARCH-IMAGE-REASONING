"""
Minimal test - just import rag module
"""
import sys
import traceback

try:
    print("Importing rag module...")
    from app.core import rag
    print("✓ Import successful")
    
    print("\nGetting embedding model...")
    model = rag.get_embedding_model()
    if model:
        print("✓ Model loaded")
        
        print("\nTesting embedding...")
        embedding = model.embed_query("test")
        print(f"✓ Embedding generated: {len(embedding)} dims")
    else:
        print("✗ Model failed to load")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
