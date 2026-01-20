"""
Simple test for sentence-transformers
"""
try:
    print("Testing sentence-transformers import...")
    from sentence_transformers import SentenceTransformer
    print("✓ Import successful")
    
    print("\nLoading model (this may take a while on first run)...")
    model = SentenceTransformer('thenlper/gte-large')
    print(f"✓ Model loaded: {model.get_sentence_embedding_dimension()} dimensions")
    
    print("\nTesting embedding generation...")
    text = "This is a test sentence."
    embedding = model.encode([text])[0]
    print(f"✓ Generated embedding: shape {embedding.shape}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
