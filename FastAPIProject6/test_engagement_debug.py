#!/usr/bin/env python3
"""
Debug Engagement Endpoints
"""

import requests

BASE_URL = "http://localhost:8001"

print("❤️ **Debugging Engagement Endpoints**")
print("=" * 40)

# Test server
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Server: {response.status_code}")
except:
    print("❌ Server not running")
    exit()

# Test all engagement endpoints
endpoints = [
    ("Engagement Stats", "/engagement/stats/public/967v5t"),
    ("Top Engaged News", "/engagement/top-engaged?limit=5"),
    ("Like Endpoint", "/engagement/like"),
    ("View Tracking", "/engagement/view/967v5t"),
    ("Share Endpoint", "/engagement/share")
]

for name, endpoint in endpoints:
    try:
        if "Like" in name or "Share" in name or "View" in name:
            # POST endpoints need data
            if "Like" in name:
                data = {"reaction_type": "like", "news_uid": "967v5t", "user_uid": "test123"}
            elif "Share" in name:
                data = {"news_uid": "967v5t", "user_uid": "test123", "platform": "whatsapp"}
            elif "View" in name:
                data = {"news_uid": "967v5t", "user_uid": "test123"}
            
            if "View" in endpoint and "/view/" in endpoint:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
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

print("\n🔍 **Checking available routes:**")
print("   Open: http://localhost:8001/docs")
print("   Look for 'engagement' section")
