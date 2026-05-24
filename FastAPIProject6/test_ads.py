#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_ad_system():
    """Complete ad system test"""
    print("📢 Testing Advertisement System...")
    
    # Test 1: View Ad Configuration
    print("\n1. Ad Configuration:")
    response = requests.get(f"{BASE_URL}/ads/config")
    if response.status_code == 200:
        config = response.json()
        print("✅ Ad Configuration:")
        print(f"   Placement interval: {config['config']['default_placement_interval']}")
        print(f"   Max ads per feed: {config['config']['max_ads_per_feed']}")
        print(f"   Ad types: {list(config['config']['ad_types'].keys())}")
    else:
        print("❌ Ad Configuration Failed")
        print(f"   Error: {response.text}")
    
    # Test 2: View All Advertisements
    print("\n2. All Advertisements:")
    response = requests.get(f"{BASE_URL}/content/advertisements")
    if response.status_code == 200:
        ads = response.json()['advertisements']
        print(f"✅ Found {len(ads)} advertisements")
        for i, ad in enumerate(ads[:3], 1):
            print(f"   {i}. 📢 {ad['title']}")
            print(f"      📝 {ad.get('content', 'No description')[:50]}...")
            print(f"      🔗 {ad.get('cta_url', 'No link')}")
    else:
        print("❌ Failed to get advertisements")
        print(f"   Error: {response.text}")
    
    # Test 3: Test Ad Placement
    print("\n3. Ad Placement Test:")
    test_data = {
        'user_uid': 'test_user_123',
        'news_count': 15,
        'placement_interval': 3,
        'max_ads': 5
    }
    
    response = requests.post(f"{BASE_URL}/ads/placement-test", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print("✅ Ad Placement Test:")
        print(f"   Total items: {result['results']['total_items']}")
        print(f"   News items: {result['results']['news_items']}")
        print(f"   Ad items: {result['results']['ad_items']}")
        print(f"   Ad ratio: {result['results']['ad_ratio']}%")
        
        # Show ad positions
        print("   📍 Ad positions:")
        for pos in result['placement_positions']:
            if pos['type'] == 'advertisement':
                print(f"      Position {pos['position']}: {pos['title']}")
    else:
        print("❌ Ad Placement Test Failed")
        print(f"   Error: {response.text}")
    
    # Test 4: Test Supported Languages
    print("\n4. Supported Languages:")
    response = requests.get(f"{BASE_URL}/ai/supported-languages")
    if response.status_code == 200:
        languages = response.json()
        print("✅ Supported Languages:")
        for lang in languages.get('languages', []):
            print(f"   🌐 {lang}")
    else:
        print("❌ Failed to get supported languages")
    
    print("\n🎉 Ad System Test Complete!")
    
    # Test 5: Test with Admin Token (if available)
    print("\n5. Admin Features (Optional):")
    print("   🔐 To test admin features, get your token from:")
    print("   http://localhost:8001/docs → Authorize → Copy token")
    print("   Then run: python admin_test.py")

if __name__ == "__main__":
    test_ad_system()
