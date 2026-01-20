
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_signup():
    print("Testing Signup...")
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 201 or "Email already registered" in response.text
    except Exception as e:
        print(f"Signup Error: {e}")
        return False

def test_login():
    print("\nTesting Login...")
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Login Error: {e}")
        return False

if __name__ == "__main__":
    if test_signup():
        test_login()
