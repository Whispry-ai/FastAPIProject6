#!/usr/bin/env python3
"""
Debug Website Issues
"""

import requests

BASE_URL = "http://localhost:8001"

print("🔍 **Debugging Website Issues**")
print("=" * 40)

# Test server
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Server: {response.status_code}")
except:
    print("❌ Server not running")
    exit()

# Test AI Analysis Client
try:
    response = requests.get(f"{BASE_URL}/ai_analysis_client.html")
    print(f"✅ AI Client Page: {response.status_code}")
    if response.status_code == 200:
        print(f"   Content length: {len(response.content)} bytes")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ AI Client Error: {e}")

# Test AI endpoints that the website uses
endpoints_to_test = [
    ("AI Test", "/ai/test-ai"),
    ("Sentiment Analysis", "/ai/sentiment-analysis"),
    ("Category Suggestion", "/ai/category-suggestion"),
    ("Fake News Detection", "/ai/fake-news-detection"),
    ("Supported Languages", "/ai/supported-languages"),
    ("CSV Template", "/ai/csv-template")
]

for name, endpoint in endpoints_to_test:
    try:
        if "POST" in name or "sentiment" in endpoint or "category" in endpoint or "fake-news" in endpoint:
            # POST endpoints
            if "sentiment" in endpoint:
                data = {"text": "This is amazing news!"}
            elif "category" in endpoint:
                data = {"text": "Tech company launches new product"}
            elif "fake-news" in endpoint:
                data = {"title": "Scientists discovery", "content": "New research shows"}
            else:
                data = {}
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            # GET endpoints
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")

print("\n🌐 **Website URLs to Test:**")
print(f"   AI Analysis Client: {BASE_URL}/ai_analysis_client.html")
print(f"   Ad Placement Client: {BASE_URL}/ad_placement_client.html")
print(f"   News Sharing Demo: {BASE_URL}/news_sharing_demo.html")
print(f"   API Documentation: {BASE_URL}/docs")
