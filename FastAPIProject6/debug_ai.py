#!/usr/bin/env python3
"""
Debug AI features step by step
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def debug_ai_features():
    """Debug AI features systematically"""
    print("🤖 **Debugging AI Features**")
    print("=" * 50)
    
    # Step 1: Check if server is running
    print("\n1. Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Step 2: Test AI endpoints
    print(f"\n2. Testing AI endpoints...")
    
    # Test sentiment analysis
    print(f"\n   2a. Testing sentiment analysis...")
    try:
        ai_data = {
            "text": "This is amazing news about technology!",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/ai/sentiment-analysis", json=ai_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Sentiment working: {result}")
        else:
            print(f"   ❌ Sentiment failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Sentiment error: {e}")
    
    # Test category suggestion
    print(f"\n   2b. Testing category suggestion...")
    try:
        category_data = {
            "text": "Tech company launches new AI product for mobile users"
        }
        response = requests.post(f"{BASE_URL}/ai/category-suggestion", json=category_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Category working: {result}")
        else:
            print(f"   ❌ Category failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Category error: {e}")
    
    # Test fake news detection
    print(f"\n   2c. Testing fake news detection...")
    try:
        fake_data = {
            "title": "Scientists Discover Revolutionary Breakthrough",
            "content": "Researchers at leading universities have announced a major breakthrough in renewable energy technology."
        }
        response = requests.post(f"{BASE_URL}/ai/fake-news-detection", json=fake_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fake news detection working: {result}")
        else:
            print(f"   ❌ Fake news detection failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Fake news detection error: {e}")
    
    # Test supported languages
    print(f"\n   2d. Testing supported languages...")
    try:
        response = requests.get(f"{BASE_URL}/ai/supported-languages")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Supported languages working: {result}")
        else:
            print(f"   ❌ Supported languages failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Supported languages error: {e}")
    
    # Test CSV template
    print(f"\n   2e. Testing CSV template...")
    try:
        response = requests.get(f"{BASE_URL}/ai/csv-template")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ CSV template working")
            print(f"   Content type: {response.headers.get('content-type')}")
        else:
            print(f"   ❌ CSV template failed: {response.text}")
    except Exception as e:
        print(f"   ❌ CSV template error: {e}")

def check_ai_routes():
    """Check if AI routes are properly registered"""
    print(f"\n3. Checking AI routes registration...")
    
    # Check if AI routes are in the docs
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
            print("   Look for 'AI' section in Swagger UI")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI error: {e}")

if __name__ == "__main__":
    debug_ai_features()
    check_ai_routes()
    
    print(f"\n🎯 **Debug Summary:**")
    print("   If AI endpoints return 404, the routes aren't loaded")
    print("   If they return 500, there's a code error")
    print("   If they return 400, there's a request format error")
    print("   Check server terminal for detailed error messages")
