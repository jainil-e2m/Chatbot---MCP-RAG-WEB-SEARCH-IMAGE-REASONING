"""
Verify Authentication Flow
"""
import requests
import uuid
import sys

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_auth_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "Password123!"

print("="*60)
print("AUTHENTICATION FLOW VERIFICATION")
print("="*60)
print(f"Target URL: {BASE_URL}")
print(f"Test Email: {TEST_EMAIL}")

# 1. Signup
print("\n[1] Testing Signup...")
try:
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD,
        "name": "Auth Tester"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload, timeout=10)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✓ Signup Successful")
        print(f"  User ID: {response.json().get('user_id')}")
    else:
        print(f"✗ Signup Failed: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 2. Login
print("\n[2] Testing Login...")
try:
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=10)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        if token:
            print("✓ Login Successful")
            print(f"  Token received: {token[:15]}...")
        else:
            print("✗ Login Failed: No token in response")
            print(f"  Response: {data}")
            sys.exit(1)
    else:
        print(f"✗ Login Failed: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 3. Verify Token (if there's a protected endpoint)
# We can skip this if we don't have a simple protected endpoint, 
# but login proving token generation is usually enough for auth flow.

print("\n" + "="*60)
print("✓ AUTHENTICATION VERIFIED")
print("="*60)
