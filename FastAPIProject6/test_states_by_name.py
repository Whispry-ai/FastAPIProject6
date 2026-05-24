#!/usr/bin/env python3
"""
Test States by Name - Show Data Format
"""

import requests

response = requests.get("http://localhost:8001/location/states")
print(f"States Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    states = data.get('states', [])
    print(f"✅ Found {len(states)} states")
    print("\n📋 **States Data Format:**")
    
    # Show raw data for first state
    if states:
        first_state = states[0]
        print(f"Raw data: {first_state}")
        print(f"\n📝 **Fields:**")
        for key, value in first_state.items():
            print(f"   {key}: {value}")
    
    print(f"\n📊 **All States:**")
    for i, state in enumerate(states):
        name = state.get('name', 'No name')
        state_id = state.get('id', 'No ID')
        print(f"   {i+1}. {name} (ID: {state_id})")
else:
    print(f"❌ Error: {response.text}")
