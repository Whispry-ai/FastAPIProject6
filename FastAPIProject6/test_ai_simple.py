#!/usr/bin/env python3
"""
Simple test to check if AI routes are loaded
"""

import requests

def test_ai_routes():
    """Test if AI routes are loaded"""
    print("🤖 **Testing AI Routes Loading**")
    print("=" * 40)
    
    # Test basic server
    try:
        response = requests.get("http://localhost:8001/")
        print(f"✅ Server status: {response.status_code}")
    except:
        print("❌ Server not accessible")
        return
    
    # Test AI test endpoint
    try:
        response = requests.get("http://localhost:8001/ai/test-ai")
        print(f"🔍 AI test endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ AI routes are loaded!")
            print(response.text)
        else:
            print(f"❌ AI test failed: {response.text}")
    except Exception as e:
        print(f"❌ AI test error: {e}")
    
    # Test supported languages (should work without auth)
    try:
        response = requests.get("http://localhost:8001/ai/supported-languages")
        print(f"🔍 Supported languages: {response.status_code}")
        if response.status_code == 200:
            print("✅ Supported languages working!")
        else:
            print(f"❌ Supported languages failed: {response.text}")
    except Exception as e:
        print(f"❌ Supported languages error: {e}")

if __name__ == "__main__":
    test_ai_routes()
