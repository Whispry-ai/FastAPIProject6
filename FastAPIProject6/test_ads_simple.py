#!/usr/bin/env python3
"""
Simple Advertisement Test - Without problematic columns
"""

import requests

BASE_URL = "http://localhost:8001"

print("📢 **Simple Advertisement Test**")
print("=" * 40)

# Test server
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Server: {response.status_code}")
except:
    print("❌ Server not running")
    exit()

# Test simple ad placement (without database issues)
print("\n🔍 **Testing Ad Placement (Simple):**")
try:
    response = requests.get(f"{BASE_URL}/ad-placement/test?user_uid=test123&news_count=5&placement_interval=3&max_ads=2")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Ad Placement Working")
        print(f"   Feed items: {len(result.get('feed', []))}")
        print(f"   Ads placed: {result.get('ads_placed', 0)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test ad placement client page
print("\n🌐 **Testing Ad Placement Client:**")
try:
    response = requests.get(f"{BASE_URL}/ad_placement_client.html")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Ad Placement Client Working")
        print(f"   Page size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test alternative ad endpoints
print("\n🔍 **Testing Alternative Ad Endpoints:**")
alt_endpoints = [
    ("Content Ads", "/content/ads"),
    ("Simple Ads", "/ads"),
    ("Ad List", "/advertisements")
]

for name, endpoint in alt_endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code == 200:
            print(f"   Working!")
    except Exception as e:
        print(f"❌ {name}: ERROR")

print("\n🎯 **Working Solutions:**")
print("1. Use ad-placement/test endpoint")
print("2. Use ad_placement_client.html page")
print("3. Check /docs for available ad endpoints")
