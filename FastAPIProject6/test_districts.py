#!/usr/bin/env python3
"""
Test Districts Endpoint
"""

import requests

# Correct URL (port 8001, single /base/ prefix)
response = requests.get("http://localhost:8001/base/districts?state_id=4&limit=100&offset=0")
print(f"Districts Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    districts = data.get('districts', [])
    print(f"✅ Found {len(districts)} districts")
    if districts:
        print(f"Sample: {districts[0].get('name', 'No name')}")
else:
    print(f"❌ Error: {response.text}")
