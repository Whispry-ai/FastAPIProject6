#!/usr/bin/env python3
"""
Debug Advertisement System
"""

import requests

BASE_URL = "http://localhost:8001"

print("📢 **Debugging Advertisement System**")
print("=" * 40)

# Test server
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Server: {response.status_code}")
except:
    print("❌ Server not running")
    exit()

# Test advertisement endpoints
endpoints = [
    ("Advertisements List", "/content/advertisements"),
    ("Ad Placement Test", "/ad-placement/test?user_uid=test123&news_count=5&placement_interval=3&max_ads=2"),
    ("Ad Placement Client", "/ad_placement_client.html")
]

for name, endpoint in endpoints:
    try:
        if "POST" in name:
            data = {"user_uid": "test123", "news_count": 5}
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code == 200:
            if "advertisements" in endpoint:
                data = response.json()
                ads = data.get('advertisements', [])
                print(f"   📢 Found {len(ads)} ads")
                if ads:
                    print(f"   Sample: {ads[0].get('title', 'No title')}")
            elif "ad-placement" in endpoint:
                data = response.json()
                feed = data.get('feed', [])
                ads_placed = data.get('ads_placed', 0)
                print(f"   📰 Feed items: {len(feed)}, Ads placed: {ads_placed}")
            elif "html" in endpoint:
                print(f"   📄 Page loaded: {len(response.content)} bytes")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")

print("\n🔍 **Checking Ad Routes:**")
print("   Open: http://localhost:8001/docs")
print("   Look for 'advertisement' or 'ad-placement' sections")
