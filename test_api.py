"""
Quick test script to verify the API endpoints are working
Run this after restarting the backend to confirm everything is set up correctly
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("🧪 Testing MADE API Endpoints")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get all OCEAN scores
    print("\n2️⃣ Testing all-ocean-scores endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/all-ocean-scores")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Count: {data.get('count', 0)}")
        if data.get('data') and len(data['data']) > 0:
            first = data['data'][0]
            print(f"   📊 First entry: {first}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
