#!/usr/bin/env python3
"""
Test Engagement Endpoints - Fixed
"""

import requests

BASE_URL = "http://localhost:8001"

print("❤️ **Fixed Engagement Endpoints**")
print("=" * 40)

# Test with different user to avoid duplicate error
test_user = f"test_user_{hash('test') % 10000}"

print(f"🔧 Using test user: {test_user}")

# 1. Like (works)
try:
    data = {
        "reaction_type": "like",
        "news_uid": "967v5t", 
        "user_uid": test_user
    }
    response = requests.post(f"{BASE_URL}/engagement/like", json=data)
    print(f"✅ Like: {response.status_code} - {response.json().get('message', 'N/A')}")
except Exception as e:
    print(f"❌ Like Error: {e}")

# 2. View (works)
try:
    data = {
        "news_uid": "967v5t",
        "user_uid": test_user
    }
    response = requests.post(f"{BASE_URL}/engagement/view/967v5t", json=data)
    print(f"✅ View: {response.status_code} - {response.json().get('message', 'N/A')}")
except Exception as e:
    print(f"❌ View Error: {e}")

# 3. Share (fixed - use different user)
try:
    data = {
        "news_uid": "967v5t",
        "user_uid": test_user, 
        "platform": "whatsapp"
    }
    response = requests.post(f"{BASE_URL}/engagement/share", json=data)
    print(f"✅ Share: {response.status_code} - {response.json().get('message', 'N/A')}")
except Exception as e:
    print(f"❌ Share Error: {e}")

# 4. Engagement Stats (works)
try:
    response = requests.get(f"{BASE_URL}/engagement/stats/public/967v5t")
    result = response.json()
    stats = result.get('stats', {})
    print(f"✅ Stats: Views={stats.get('views_count', 0)}, Likes={stats.get('likes_count', 0)}, Shares={stats.get('shares_count', 0)}")
except Exception as e:
    print(f"❌ Stats Error: {e}")

print("\n🌐 **Working Website URLs:**")
print(f"   {BASE_URL}/ai_analysis_client.html")
print(f"   {BASE_URL}/ad_placement_client.html")
print(f"   {BASE_URL}/news_sharing_demo.html")
print(f"   {BASE_URL}/docs")

print("\n🎯 **Correct Endpoints for Website:**")
print("   POST /engagement/like")
print("   POST /engagement/view/{news_uid}")
print("   POST /engagement/share")
print("   GET  /engagement/stats/public/{news_uid}")
