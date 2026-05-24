#!/usr/bin/env python3
"""
How to Watch and Test Advertisements
Complete guide to viewing and testing the ad system
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def show_ad_watching_methods():
    """Show different ways to watch ads"""
    print("📢 **How to Watch and Test Advertisements**")
    print("=" * 60)
    
    print("\n🎯 **Available Methods to Watch Ads:**")
    print("-" * 50)
    
    methods = [
        {
            "method": "View Ad Configuration",
            "description": "See current ad placement settings",
            "endpoint": "GET /ads/config",
            "auth": "Not required"
        },
        {
            "method": "Get Targeted Ads",
            "description": "Get personalized ads for your location/preferences",
            "endpoint": "GET /ads/targeted",
            "auth": "Required"
        },
        {
            "method": "View All Advertisements",
            "description": "Browse all available ads with filtering",
            "endpoint": "GET /content/advertisements",
            "auth": "Not required"
        },
        {
            "method": "Test Ad Placement",
            "description": "See how ads appear in news feed",
            "endpoint": "POST /ads/placement-test",
            "auth": "Not required"
        },
        {
            "method": "View Ad Performance",
            "description": "See ad analytics and performance metrics",
            "endpoint": "GET /ads/analytics/overview",
            "auth": "Required"
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. **{method['method']}**")
        print(f"   📝 {method['description']}")
        print(f"   🔗 {method['endpoint']}")
        print(f"   🔐 Auth: {method['auth']}")

def show_ad_placement_logic():
    """Show how ad placement works"""
    print("\n🎯 **Ad Placement Logic - How Ads Appear**")
    print("=" * 50)
    
    print("\n**Default Placement Strategy:**")
    print("-" * 40)
    print("   📰 Position 1: News Article")
    print("   📰 Position 2: News Article")
    print("   📰 Position 3: News Article")
    print("   📢 Position 4: ADVERTISEMENT")
    print("   📰 Position 5: News Article")
    print("   📰 Position 6: News Article")
    print("   📰 Position 7: News Article")
    print("   📢 Position 8: ADVERTISEMENT")
    print("   🔄 Pattern continues...")
    
    print("\n**Placement Rules:**")
    print("-" * 40)
    print("   🎯 Every 3 news articles: Insert 1 ad")
    print("   📊 Maximum 5 ads per feed: Prevents overload")
    print("   📍 Targeted selection: Based on user location")
    print("   ⭐ Priority ordering: Higher priority ads first")
    print("   🔄 Smart rotation: Different ads each time")

def show_testing_examples():
    """Show practical testing examples"""
    print("\n🧪 **Testing Advertisement System**")
    print("=" * 50)
    
    print("\n**Example 1: View Ad Configuration (No Auth)**")
    print("```bash")
    print("curl http://localhost:8001/ads/config")
    print("```")
    print("")
    print("```python")
    print("import requests")
    print("response = requests.get('http://localhost:8001/ads/config')")
    print("print(response.json())")
    print("```")
    
    print("\n**Example 2: View All Advertisements (No Auth)**")
    print("```python")
    print("# Get all ads with filtering")
    print("response = requests.get(")
    print("    'http://localhost:8001/content/advertisements',")
    print("    params={'active_only': True, 'limit': 10}")
    print(")")
    print("ads = response.json()['advertisements']")
    print("for ad in ads:")
    print("    print(f\"📢 {ad['title']} - {ad['cta_text']}\")")
    print("```")
    
    print("\n**Example 3: Get Targeted Ads (Auth Required)**")
    print("```python")
    print("# Use your admin token")
    print("token = 'YOUR_ADMIN_TOKEN'")
    print("headers = {'Authorization': f'Bearer {token}'}")
    print("")
    print("response = requests.get(")
    print("    'http://localhost:8001/ads/targeted',")
    print("    headers=headers")
    print(")")
    print("targeted_ads = response.json()['ads']")
    print("for ad in targeted_ads:")
    print("    print(f\"🎯 Targeted Ad: {ad['title']}\")")
    print("    print(f\"   Relevance: {ad['relevance_score']}\")")
    print("```")
    
    print("\n**Example 4: Test Ad Placement in News Feed**")
    print("```python")
    print("# Test how ads appear in news feed")
    print("test_data = {")
    print("    'user_uid': 'test_user_123',")
    print("    'news_count': 20,")
    print("    'placement_interval': 3,")
    print("    'max_ads': 5")
    print("}")
    print("")
    print("response = requests.post(")
    print("    'http://localhost:8001/ads/placement-test',")
    print("    json=test_data")
    print(")")
    print("")
    print("result = response.json()")
    print("print(f\"Total items: {result['results']['total_items']}\")")
    print("print(f\"News items: {result['results']['news_items']}\")")
    print("print(f\"Ad items: {result['results']['ad_items']}\")")
    print("")
    print("# Show ad positions")
    print("for position in result['placement_positions']:")
    print("    if position['type'] == 'advertisement':")
    print("        print(f\"📢 Ad at position {position['position']}: {position['title']}\")")
    print("```")

def show_swagger_testing():
    """Show how to test ads in Swagger UI"""
    print("\n🌐 **Testing Ads in Swagger UI**")
    print("=" * 40)
    
    print("\n**Step-by-Step:**")
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔐 Authorize as admin (or skip for public endpoints)")
    print("3. 🔍 Find 'Ad Placement' or 'Content Enhanced' sections")
    print("4. 🧪 Test different endpoints")
    
    print("\n**Recommended Endpoints to Test:**")
    swagger_tests = [
        {
            "section": "Ad Placement",
            "endpoint": "GET /ads/config",
            "description": "View ad configuration",
            "auth": "Not required"
        },
        {
            "section": "Ad Placement", 
            "endpoint": "POST /ads/placement-test",
            "description": "Test ad placement in feed",
            "auth": "Not required"
        },
        {
            "section": "Content Enhanced",
            "endpoint": "GET /content/advertisements",
            "description": "View all advertisements",
            "auth": "Not required"
        },
        {
            "section": "Ad Placement",
            "endpoint": "GET /ads/targeted", 
            "description": "Get personalized ads",
            "auth": "Required"
        }
    ]
    
    for test in swagger_tests:
        print(f"\n   📍 {test['section']}")
        print(f"      🔗 {test['endpoint']}")
        print(f"      📝 {test['description']}")
        print(f"      🔐 Auth: {test['auth']}")

def show_ad_analytics():
    """Show how to view ad analytics"""
    print("\n📊 **Viewing Advertisement Analytics**")
    print("=" * 50)
    
    print("\n**Available Analytics:**")
    analytics_types = [
        {
            "type": "Ad Performance",
            "endpoint": "GET /ads/performance/{ad_id}",
            "description": "View performance of specific ad",
            "data": "Impressions, clicks, CTR, revenue"
        },
        {
            "type": "Overall Analytics",
            "endpoint": "GET /ads/analytics/overview", 
            "description": "Complete ad system overview",
            "data": "Total ads, active ads, performance metrics"
        },
        {
            "type": "Placement Strategy",
            "endpoint": "GET /ads/strategy/optimize",
            "description": "Get optimized placement strategy",
            "data": "Best intervals, targeting weights"
        }
    ]
    
    for analytic in analytics_types:
        print(f"\n📈 {analytic['type']}:")
        print(f"   🔗 {analytic['endpoint']}")
        print(f"   📝 {analytic['description']}")
        print(f"   📊 Data: {analytic['data']}")
    
    print("\n**Example - View Ad Analytics:**")
    print("```python")
    print("# Get overall ad analytics")
    print("token = 'YOUR_ADMIN_TOKEN'")
    print("headers = {'Authorization': f'Bearer {token}'}")
    print("")
    print("response = requests.get(")
    print("    'http://localhost:8001/ads/analytics/overview',")
    print("    headers=headers")
    print(")")
    print("")
    print("analytics = response.json()")
    print("print(f\"Total ads: {analytics['summary']['total_ads']}\")")
    print("print(f\"Active ads: {analytics['summary']['active_ads']}\")")
    print("print(f\"Total impressions: {analytics['summary']['total_impressions']}\")")
    print("```")

def create_ad_test_script():
    """Create a comprehensive ad testing script"""
    print("\n🚀 **Complete Ad Testing Script**")
    print("=" * 40)
    
    script_content = '''
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_ad_system():
    """Complete ad system test"""
    print("📢 Testing Advertisement System...")
    
    # Test 1: View Ad Configuration
    print("\\n1. Ad Configuration:")
    response = requests.get(f"{BASE_URL}/ads/config")
    if response.status_code == 200:
        config = response.json()
        print("✅ Ad Configuration:")
        print(f"   Placement interval: {config['config']['default_placement_interval']}")
        print(f"   Max ads per feed: {config['config']['max_ads_per_feed']}")
    else:
        print("❌ Ad Configuration Failed")
    
    # Test 2: View All Advertisements
    print("\\n2. All Advertisements:")
    response = requests.get(f"{BASE_URL}/content/advertisements")
    if response.status_code == 200:
        ads = response.json()['advertisements']
        print(f"✅ Found {len(ads)} advertisements")
        for i, ad in enumerate(ads[:3], 1):
            print(f"   {i}. 📢 {ad['title']}")
            print(f"      📝 {ad.get('content', 'No description')[:50]}...")
    else:
        print("❌ Failed to get advertisements")
    
    # Test 3: Test Ad Placement
    print("\\n3. Ad Placement Test:")
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
    
    print("\\n🎉 Ad System Test Complete!")

if __name__ == "__main__":
    test_ad_system()
'''
    
    print("Create `test_ads.py` with this content:")
    print("```python")
    print(script_content)
    print("```")
    print("Then run: python test_ads.py")

def main():
    """Main function"""
    print("📢 **Complete Guide to Watching and Testing Advertisements**")
    print("=" * 70)
    print("Here's how to view, test, and analyze the advertisement system.")
    print()
    
    show_ad_watching_methods()
    show_ad_placement_logic()
    show_testing_examples()
    show_swagger_testing()
    show_ad_analytics()
    create_ad_test_script()
    
    print(f"\n🎯 **Quick Start to Watch Ads:**")
    print("=" * 40)
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔍 Find 'Ad Placement' or 'Content Enhanced' sections")
    print("3. 🧪 Try 'GET /ads/config' (no auth needed)")
    print("4. 🧪 Try 'GET /content/advertisements' (no auth needed)")
    print("5. 🧪 Try 'POST /ads/placement-test' (no auth needed)")
    print("6. 🔐 For advanced: Authorize and try 'GET /ads/targeted'")
    
    print(f"\n💡 **What You'll See:**")
    print("=" * 30)
    print("📢 Ad configuration and placement rules")
    print("🎯 Targeted advertisements based on location")
    print("📊 Ad performance and analytics")
    print("🔄 How ads appear in news feeds")
    print("📈 Revenue and engagement metrics")

if __name__ == "__main__":
    main()
