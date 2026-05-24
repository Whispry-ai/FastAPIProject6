#!/usr/bin/env python3
"""
Test CSV export with authentication
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_csv_export():
    """Test CSV export endpoints with authentication"""
    print("📊 **Testing CSV Export with Authentication**")
    print("=" * 50)
    
    # Step 1: Login as admin to get token
    print("\n1. Logging in as admin...")
    try:
        login_data = {
            "username": "ADMIN001",
            "password": "admin123"  # Default admin password
        }
        
        response = requests.post(f"{BASE_URL}/user/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print(f"✅ Login successful, got token")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test CSV export with token
    print(f"\n2. Testing CSV export with token...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/csv/export-categories", headers=headers)
        if response.status_code == 200:
            print(f"✅ CSV export successful")
            print(f"   Content type: {response.headers.get('content-type')}")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"❌ CSV export failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ CSV export error: {e}")
    
    # Step 3: Test engagement endpoints with token
    print(f"\n3. Testing engagement endpoints...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        
        # Test top engaged news
        response = requests.get(f"{BASE_URL}/engagement/top-engaged?limit=5", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Top engaged news: {len(result.get('news', []))} articles")
        else:
            print(f"❌ Top engaged failed: {response.status_code} - {response.text}")
        
        # Test engagement stats
        response = requests.get(f"{BASE_URL}/engagement/stats/public/967v5t", headers=headers)
        if response.status_code == 200:
            result = response.json()
            stats = result.get('stats', {})
            print(f"✅ Engagement stats: Views={stats.get('views_count', 0)}, Likes={stats.get('likes_count', 0)}")
        else:
            print(f"❌ Engagement stats failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Engagement test error: {e}")
    
    print(f"\n🎉 **Test Complete!**")

if __name__ == "__main__":
    test_csv_export()
