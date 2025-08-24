#!/usr/bin/env python3
"""
Quick test of ML API with authentication without Django setup
"""

import requests

# Test the ML API directly
ML_API_BASE_URL = "http://139.84.137.195:8001"
ML_API_KEY = "supersecrettoken123"


def test_ml_api():
    """Test ML API with authentication"""
    print("🔑 Testing ML API Authentication")
    print(f"API Base URL: {ML_API_BASE_URL}")
    print(f"API Key: {ML_API_KEY}")

    # Test data
    test_data = {"url": "https://example.com/test.jpg"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ML_API_KEY}",
        "X-API-Key": ML_API_KEY,
    }

    # Test identify-pet endpoint
    print("\n🔍 Testing identify-pet endpoint...")
    try:
        response = requests.post(
            f"{ML_API_BASE_URL}/identify-pet/",
            json=test_data,
            headers=headers,
            timeout=10,
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            print("✅ API authentication working!")
        else:
            print("⚠️ API returned non-200 status")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test generate-embedding endpoint
    print("\n🧮 Testing generate-embedding endpoint...")
    try:
        response = requests.post(
            f"{ML_API_BASE_URL}/generate-embedding/",
            json=test_data,
            headers=headers,
            timeout=10,
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            print("✅ API authentication working!")
            # Check embedding dimensions
            try:
                data = response.json()
                if "embedding" in data:
                    embedding = data["embedding"]
                    print(f"📊 Embedding dimensions: {len(embedding)}")
                    if len(embedding) == 512:
                        print(
                            "ℹ️ API returns 512-dimensional embeddings (need to truncate to 384)"
                        )
                    elif len(embedding) == 384:
                        print(
                            "✅ API returns 384-dimensional embeddings (perfect match)"
                        )
                    else:
                        print(f"⚠️ Unexpected embedding dimensions: {len(embedding)}")
            except:
                print("⚠️ Could not parse embedding from response")
        else:
            print("⚠️ API returned non-200 status")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_ml_api()
