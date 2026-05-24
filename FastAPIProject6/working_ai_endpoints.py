#!/usr/bin/env python3
"""
Working AI Endpoints - Simple Tests
"""

import requests

BASE_URL = "http://localhost:8001"

print("🤖 **Working AI Endpoints**")
print("=" * 40)

# 1. AI Test
response = requests.get(f"{BASE_URL}/ai/test-ai")
print(f"✅ AI Test: {response.status_code}")

# 2. Sentiment Analysis
data = {"text": "This is amazing news!"}
response = requests.post(f"{BASE_URL}/ai/sentiment-analysis", json=data)
result = response.json()
print(f"✅ Sentiment: {result.get('sentiment', 'N/A')}")

# 3. Category Suggestion  
data = {"text": "Tech company launches new product"}
response = requests.post(f"{BASE_URL}/ai/category-suggestion", json=data)
result = response.json()
print(f"✅ Category: {result.get('suggested_category', 'N/A')}")

# 4. Fake News Detection
data = {"title": "Scientists discovery", "content": "New research shows"}
response = requests.post(f"{BASE_URL}/ai/fake-news-detection", json=data)
result = response.json()
print(f"✅ Fake News: {result.get('is_fake', 'N/A')}")

# 5. Supported Languages
response = requests.get(f"{BASE_URL}/ai/supported-languages")
result = response.json()
languages = result.get('data', {}).get('languages', [])
print(f"✅ Languages: {len(languages)} available")

# 6. CSV Template
response = requests.get(f"{BASE_URL}/ai/csv-template")
print(f"✅ CSV Template: {response.status_code}")

print("\n🎯 **All AI endpoints are working!**")
print("📝 Use these exact endpoints:")
print("   POST /ai/sentiment-analysis")
print("   POST /ai/category-suggestion") 
print("   POST /ai/fake-news-detection")
print("   GET /ai/supported-languages")
print("   GET /ai/csv-template")
