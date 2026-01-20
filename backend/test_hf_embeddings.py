"""
Test HuggingFace embeddings directly
"""
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
import os

# Test with demo key
api_key = os.getenv("HUGGINGFACE_API_KEY", "hf_demo")

print("Testing HuggingFace Inference API...")
print(f"API Key: {api_key[:10]}...")

try:
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=api_key,
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    print("\nGenerating embedding for test text...")
    test_text = "This is a test sentence."
    
    embedding = embeddings.embed_query(test_text)
    
    print(f"✓ Embedding generated!")
    print(f"  Type: {type(embedding)}")
    print(f"  Length: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
