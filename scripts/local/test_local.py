#!/usr/bin/env python3
"""
Test script to verify local serverless setup
"""
import requests
import json
import time

def test_api():
    """Test the local API endpoints"""
    base_url = "http://localhost:3000"
    
    print("🧪 Testing Local Serverless API...")
    print("-" * 40)
    
    # Test health endpoint
    try:
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print("\nMake sure the server is running with: npm start")
        return
    
    # Test API info
    try:
        print("\nTesting /api/v1 endpoint...")
        response = requests.get(f"{base_url}/api/v1")
        if response.status_code == 200:
            print(f"✅ API info: {response.json()}")
        else:
            print(f"⚠️  API info returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 40)
    print("✅ Local testing complete!")
    print(f"\n📍 API is running at: {base_url}")
    print("📚 Try these endpoints:")
    print(f"  - {base_url}/health")
    print(f"  - {base_url}/api/v1")
    print(f"  - {base_url}/docs (API documentation)")

if __name__ == "__main__":
    test_api()
