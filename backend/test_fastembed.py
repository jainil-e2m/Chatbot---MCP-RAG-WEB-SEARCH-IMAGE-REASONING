"""
Test FastEmbed directly
"""
try:
    print("Testing FastEmbed import...")
    from fastembed import TextEmbedding
    print("✓ Import successful")
    
    print("\nLoading model...")
    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("✓ Model loaded")
    
    print("\nTesting embedding generation...")
    text = ["This is a test sentence."]
    embeddings = list(model.embed(text))
    embedding = embeddings[0]
    print(f"✓ Generated embedding: shape {len(embedding)}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
