"""
Test script to verify backend is working
Run this to test if backend endpoints respond correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(url, method="GET", data=None):
    """Test an endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {url}")
        print(f"Status: {response.status_code}")
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text[:200]}")
        print(f"{'='*60}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {url}")
        print("   Backend server is not running or crashed!")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Backend Endpoints...")
    print("="*60)
    
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    test_endpoint(f"{BASE_URL}/health")
    
    # Test available models
    print("\n2. Testing /api/v1/suppliers/available-models endpoint...")
    test_endpoint(f"{BASE_URL}/api/v1/suppliers/available-models")
    
    # Test evaluate endpoint
    print("\n3. Testing /api/v1/suppliers/evaluate endpoint...")
    test_endpoint(
        f"{BASE_URL}/api/v1/suppliers/evaluate",
        method="POST",
        data={"model_type": "xgboost", "supplier_ids": None}
    )
    
    print("\n" + "="*60)
    print("Testing complete!")

