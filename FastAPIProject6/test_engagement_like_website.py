#!/usr/bin/env python3
"""
Test Engagement Like Website Calls
"""

import requests

BASE_URL = "http://localhost:8001"

print("❤️ **Testing Engagement Like (Website Style)**")
print("=" * 50)

# Test Like exactly like website would call it
try:
    data = {
        "reaction_type": "like",
        "news_uid": "967v5t", 
        "user_uid": "test123"
    }
    response = requests.post(f"{BASE_URL}/engagement/like", json=data)
    print(f"✅ Like Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Like Error: {e}")

print("\n👁️ **Testing View Tracking (Website Style)**")
print("=" * 50)

# Test View exactly like website would call it
try:
    data = {
        "news_uid": "967v5t",
        "user_uid": "test123"
    }
    response = requests.post(f"{BASE_URL}/engagement/view/967v5t", json=data)
    print(f"✅ View Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ View Error: {e}")

print("\n📤 **Testing Share (Website Style)**")
print("=" * 50)

# Test Share exactly like website would call it
try:
    data = {
        "news_uid": "967v5t",
        "user_uid": "test123", 
        "platform": "whatsapp"
    }
    response = requests.post(f"{BASE_URL}/engagement/share", json=data)
    print(f"✅ Share Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Share Error: {e}")

print("\n🌐 **Website URLs to Test:**")
print(f"   AI Analysis Client: {BASE_URL}/ai_analysis_client.html")
print(f"   Ad Placement Client: {BASE_URL}/ad_placement_client.html")
print(f"   News Sharing Demo: {BASE_URL}/news_sharing_demo.html")
print(f"   API Documentation: {BASE_URL}/docs")
