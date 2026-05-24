#!/usr/bin/env python3
"""
Test Advertisement System - Correct Endpoints
"""

import requests

BASE_URL = "http://localhost:8001"

print("📢 **Testing Advertisement System (Correct Endpoints)**")
print("=" * 50)

# Test server
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Server: {response.status_code}")
except:
    print("❌ Server not running")
    exit()

# Test correct ad placement endpoints
endpoints = [
    ("Targeted Ads", "/ads/targeted"),
    ("Ad Placement Test", "/ads/placement-test"),
    ("Ad Performance", "/ads/performance/1"),
    ("Ad Strategy", "/ads/strategy/optimize"),
    ("Ad Analytics", "/ads/analytics/overview")
]

print("\n🔍 **Testing Ad Placement Endpoints:**")
for name, endpoint in endpoints:
    try:
        if "placement-test" in endpoint:
            # POST endpoint
            data = {"user_uid": "test123", "news_count": 5, "placement_interval": 3}
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            # GET endpoints
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if "ads" in result:
                print(f"   📢 Found {len(result.get('ads', []))} ads")
            elif "feed" in result:
                print(f"   📰 Feed items: {len(result.get('feed', []))}")
            else:
                print(f"   ✅ Working")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")

# Test ad placement client page
print("\n🌐 **Testing Ad Placement Client Page:**")
try:
    response = requests.get(f"{BASE_URL}/ad_placement_client.html")
    print(f"✅ Ad Placement Client: {response.status_code}")
    if response.status_code == 200:
        print(f"   Page size: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ Ad Placement Client Error: {e}")

print("\n🎯 **Correct Ad Endpoints:**")
print("   POST /ads/placement-test")
print("   GET  /ads/targeted")
print("   GET  /ads/performance/{ad_id}")
print("   GET  /ads/strategy/optimize")
print("   GET  /ads/analytics/overview")

print("\n🌐 **Working URLs:**")
print(f"   {BASE_URL}/ad_placement_client.html")
print(f"   {BASE_URL}/docs")
