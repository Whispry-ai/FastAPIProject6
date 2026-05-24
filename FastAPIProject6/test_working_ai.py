#!/usr/bin/env python3
"""
Test Working AI Endpoints
"""

import requests

BASE_URL = "http://localhost:8001"

# Test working AI endpoints
endpoints = [
    ("AI Test", "/ai/test-ai"),
    ("AI Sentiment", "/ai/sentiment-analysis"),
    ("AI Category", "/ai/category-suggestion"),
    ("AI Fake News", "/ai/fake-news-detection"),
    ("AI Languages", "/ai/supported-languages"),
    ("AI CSV Template", "/ai/csv-template")
]

print("🤖 **Testing AI Endpoints**")
print("=" * 40)

for name, endpoint in endpoints:
    try:
        if "POST" in name or "sentiment" in endpoint or "category" in endpoint or "fake-news" in endpoint:
            # POST endpoints need data
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
        if response.status_code == 200:
            result = response.json()
            if "message" in result:
                print(f"   📝 {result.get('message', '')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
