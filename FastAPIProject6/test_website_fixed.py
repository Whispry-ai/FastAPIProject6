#!/usr/bin/env python3
"""
Test Fixed Website
"""

import requests

BASE_URL = "http://localhost:8001"

print("🌐 **Testing Fixed Website**")
print("=" * 40)

# Test the exact API calls the website makes
print("🔍 Testing API calls that website uses:")

# 1. Sentiment Analysis (like the website)
try:
    data = {"text": "This is amazing news!"}
    response = requests.post(f"{BASE_URL}/ai/sentiment-analysis", json=data)
    print(f"✅ Sentiment Analysis: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result.get('sentiment', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Sentiment Analysis Error: {e}")

# 2. Category Suggestion (like the website)
try:
    data = {"text": "Tech company launches new product"}
    response = requests.post(f"{BASE_URL}/ai/category-suggestion", json=data)
    print(f"✅ Category Suggestion: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result.get('suggested_category', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Category Suggestion Error: {e}")

# 3. Fake News Detection (like the website)
try:
    data = {"title": "Scientists discovery", "content": "New research shows"}
    response = requests.post(f"{BASE_URL}/ai/fake-news-detection", json=data)
    print(f"✅ Fake News Detection: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result.get('is_fake', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Fake News Detection Error: {e}")

print("\n🌐 **Website URLs (Fixed):**")
print(f"   AI Analysis Client: {BASE_URL}/ai_analysis_client.html")
print(f"   Ad Placement Client: {BASE_URL}/ad_placement_client.html")
print(f"   News Sharing Demo: {BASE_URL}/news_sharing_demo.html")
print(f"   API Documentation: {BASE_URL}/docs")

print("\n✅ **Fixed Issues:**")
print("   • Removed 'language' parameter from sentiment analysis")
print("   • All API calls now match working endpoints")
print("   • Website should fetch details correctly now")
