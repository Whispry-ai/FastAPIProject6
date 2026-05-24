#!/usr/bin/env python3
"""
Test Working States Endpoint
"""

import requests

response = requests.get("http://localhost:8001/location/states")
print(f"States Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    states = data.get('states', [])
    print(f"✅ Found {len(states)} states")
    if states:
        print(f"Sample state: {states[0].get('name', 'No name')} (ID: {states[0].get('id', 'No ID')})")
        # Show first 3 states
        for i, state in enumerate(states[:3]):
            print(f"   {i+1}. {state.get('name', 'No name')} - ID: {state.get('id', 'No ID')}")
else:
    print(f"❌ Error: {response.text}")
