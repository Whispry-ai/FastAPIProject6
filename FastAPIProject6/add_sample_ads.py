#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def add_sample_ads():
    """Add sample advertisements to see them in the feed"""
    print("📢 Adding Sample Advertisements...")
    
    # Sample ads data
    sample_ads = [
        {
            "title": "Special Offer - Local Business",
            "content": "Get 20% off at your favorite local restaurant!",
            "image_url": "https://example.com/restaurant-ad.jpg",
            "redirect_url": "https://local-restaurant.com",
            "placement": "sidebar",
            "start_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "state_id": 1,
            "target_gender": None,
            "target_age_min": None,
            "target_age_max": None,
            "is_premium": False,
            "premium_priority": 1
        },
        {
            "title": "New Tech Product Launch",
            "content": "Discover the latest smartphone with amazing features!",
            "image_url": "https://example.com/tech-ad.jpg",
            "redirect_url": "https://tech-store.com",
            "placement": "in_feed",
            "start_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "state_id": 1,
            "target_gender": None,
            "target_age_min": 18,
            "target_age_max": 65,
            "is_premium": True,
            "premium_priority": 5
        },
        {
            "title": "Community Event Promotion",
            "content": "Join us for the annual community festival this weekend!",
            "image_url": "https://example.com/event-ad.jpg",
            "redirect_url": "https://community-festival.com",
            "placement": "in_feed",
            "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=10)).isoformat(),
            "state_id": 1,
            "target_gender": None,
            "target_age_min": None,
            "target_age_max": None,
            "is_premium": False,
            "premium_priority": 2
        }
    ]
    
    # Add each ad
    added_count = 0
    for i, ad_data in enumerate(sample_ads, 1):
        print(f"\n{i}. Adding: {ad_data['title']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/content/advertisements",
                json=ad_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Added successfully: {result.get('success', False)}")
                added_count += 1
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎉 Added {added_count} sample advertisements!")
    
    # Test ad placement again
    print(f"\n🧪 Testing Ad Placement with New Ads:")
    test_data = {
        'user_uid': 'test123',
        'news_count': 10,
        'placement_interval': 3,
        'max_ads': 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ads/placement-test", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Total items: {result['results']['total_items']}")
            print(f"✅ News items: {result['results']['news_items']}")
            print(f"✅ Ad items: {result['results']['ad_items']}")
            print(f"✅ Ad ratio: {result['results']['ad_ratio']}%")
            
            # Show ad positions
            print(f"\n📢 Feed Layout:")
            for pos in result['placement_positions']:
                icon = "🔴" if pos['type'] == 'advertisement' else "🟢"
                print(f"   {icon} {pos['type'].upper()} - Position {pos['position']}")
                print(f"      {pos.get('title', 'No title')}")
                
        else:
            print(f"❌ Ad placement test failed: {response.text}")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    add_sample_ads()
