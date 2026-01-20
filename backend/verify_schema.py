"""
Verify Supabase Schema Dimensions
"""
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("="*60)
print("SCHEMA VERIFICATION")
print("="*60)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# 1. Try to insert a dummy embedding of size 1536
print("\n[1] Testing 1536-dim insert...")
dummy_embedding_1536 = [0.1] * 1536
data_1536 = {
    "conversation_id": "test_schema_check",
    "content": "Schema Check 1536",
    "embedding": dummy_embedding_1536,
    "metadata": {"type": "probe_1536"}
}

try:
    resp = httpx.post(
        f"{SUPABASE_URL}/rest/v1/documents",
        headers=headers,
        json=data_1536,
        timeout=30.0
    )
    if resp.status_code in [200, 201]:
        print("✓ SUCCESS: Database accepts 1536 dimensions.")
        # Cleanup
        httpx.delete(f"{SUPABASE_URL}/rest/v1/documents?conversation_id=eq.test_schema_check", headers=headers)
    else:
        print(f"✗ FAILED to insert 1536 dims: {resp.status_code} - {resp.text}")
        
        # 2. Try 384 dims (fallback check)
        print("\n[2] Testing 384-dim insert (Fallback check)...")
        dummy_embedding_384 = [0.1] * 384
        data_384 = {
            "conversation_id": "test_schema_check",
            "content": "Schema Check 384",
            "embedding": dummy_embedding_384,
            "metadata": {"type": "probe_384"}
        }
        resp_384 = httpx.post(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers=headers,
            json=data_384,
            timeout=30.0
        )
        if resp_384.status_code in [200, 201]:
            print("! DETECTED: Database still expects 384 dimensions!")
            print("  ACTION REQUIRED: Run the updated schema.sql to switch to 1536 dimensions.")
            # Cleanup
            httpx.delete(f"{SUPABASE_URL}/rest/v1/documents?conversation_id=eq.test_schema_check", headers=headers)
        else:
            print(f"✗ FAILED to insert 384 dims too: {resp_384.status_code} - {resp_384.text}")

except Exception as e:
    print(f"✗ Error: {e}")
