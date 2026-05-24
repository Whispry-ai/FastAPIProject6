#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_simple_ads():
    """Simple ad system test without database dependencies"""
    print("📢 Simple Advertisement System Test...")
    
    # Test 1: Ad Configuration (should work)
    print("\n1. Ad Configuration:")
    try:
        response = requests.get(f"{BASE_URL}/ads/config")
        if response.status_code == 200:
            config = response.json()
            print("✅ Ad Configuration:")
            print(f"   Placement interval: {config['config']['default_placement_interval']}")
            print(f"   Max ads per feed: {config['config']['max_ads_per_feed']}")
            print(f"   Ad types: {list(config['config']['ad_types'].keys())}")
        else:
            print("❌ Ad Configuration Failed")
    except Exception as e:
        print(f"❌ Ad Configuration Error: {e}")
    
    # Test 2: Health Check (should work)
    print("\n2. Server Health:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Get Categories (should work)
    print("\n3. News Categories:")
    try:
        response = requests.get(f"{BASE_URL}/news/categories")
        if response.status_code == 200:
            print("✅ News categories accessible")
        else:
            print("❌ News categories failed")
    except Exception as e:
        print(f"❌ Categories error: {e}")
    
    # Test 4: Location States (should work)
    print("\n4. Location States:")
    try:
        response = requests.get(f"{BASE_URL}/location/states")
        if response.status_code == 200:
            print("✅ Location states accessible")
        else:
            print("❌ Location states failed")
    except Exception as e:
        print(f"❌ Location error: {e}")
    
    # Test 5: Ad Placement Test (might work now)
    print("\n5. Ad Placement Test:")
    try:
        test_data = {
            'user_uid': 'test123',
            'news_count': 10,
            'placement_interval': 3,
            'max_ads': 3
        }
        
        response = requests.post(f"{BASE_URL}/ads/placement-test", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Ad Placement Test:")
            print(f"   Total items: {result['results']['total_items']}")
            print(f"   News items: {result['results']['news_items']}")
            print(f"   Ad items: {result['results']['ad_items']}")
        else:
            print(f"❌ Ad Placement Test Failed: {response.text}")
    except Exception as e:
        print(f"❌ Ad placement error: {e}")
    
    print("\n🎉 Simple Ad Test Complete!")
    
    # Test 6: Show what to expect
    print("\n📋 What to Expect:")
    print("=" * 30)
    print("📢 Ad Configuration: Placement rules and settings")
    print("🎯 Ad Placement: How ads appear in news feed")
    print("📰 News Categories: Available news categories")
    print("📍 Location States: Available states for targeting")
    
    print("\n🔧 If Issues Persist:")
    print("=" * 30)
    print("• Check server is running: python -m uvicorn main:app --port 8001")
    print("• Check database connection and schema")
    print("• Try Swagger UI: http://localhost:8001/docs")
    print("• Test individual endpoints there")

if __name__ == "__main__":
    test_simple_ads()
