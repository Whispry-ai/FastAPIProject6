#!/usr/bin/env python3
"""
Test All Location Endpoints
"""

import requests

BASE_URL = "http://localhost:8001"

endpoints = [
    ("States", "/base/states"),
    ("Districts", "/base/districts"),
    ("Cities", "/base/cities"),
    ("Location States", "/location/states"),
    ("Location Districts", "/location/districts"),
    ("Location Cities", "/location/cities")
]

print("📍 **Testing Location Endpoints**")
print("=" * 40)

for name, endpoint in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
