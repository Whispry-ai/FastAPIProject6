#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def view_existing_news():
    """View your existing 9 news articles and test ad placement"""
    print("📰 Viewing Your Existing News Articles...")
    
    # Test 1: Get All News (should show your 9 articles)
    print("\n1. All Published News:")
    response = requests.get(f"{BASE_URL}/news")
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('news', [])
        print(f"✅ Found {len(articles)} news articles")
        
        print("\n📋 Your News Articles:")
        for i, article in enumerate(articles, 1):
            print(f"   {i}. 📰 {article.get('title', 'No title')}")
            print(f"      👁️ Views: {article.get('views_count', 0)}")
            print(f"      ❤️ Likes: {article.get('likes_count', 0)}")
            print(f"      📅 Created: {article.get('created_at', 'N/A')}")
            print()
    else:
        print("❌ Failed to get news")
        return
    
    # Test 2: Test Ad Placement with your existing news
    print("2. Ad Placement Test with Your News:")
    test_data = {
        'user_uid': 'test123',
        'news_count': 9,  # Use your exact news count
        'placement_interval': 3,
        'max_ads': 3
    }
    
    response = requests.post(f"{BASE_URL}/ads/placement-test", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Total items: {result['results']['total_items']}")
        print(f"✅ News items: {result['results']['news_items']}")
        print(f"✅ Ad items: {result['results']['ad_items']}")
        print(f"✅ Ad ratio: {result['results']['ad_ratio']}%")
        
        # Show the complete feed layout
        print(f"\n📊 Complete Feed Layout:")
        print("=" * 50)
        for pos in result['placement_positions']:
            icon = "🔴" if pos['type'] == 'advertisement' else "🟢"
            print(f"   {icon} {pos['type'].upper()} - Position {pos['position']}")
            if pos['type'] == 'news':
                print(f"      📰 {pos.get('title', 'No title')}")
            else:
                print(f"      📢 {pos.get('title', 'Advertisement')}")
            print()
    else:
        print(f"❌ Ad placement test failed: {response.text}")
    
    # Test 3: Show trending news
    print("3. Trending News:")
    response = requests.get(f"{BASE_URL}/news/trending")
    if response.status_code == 200:
        trending = response.json().get('news', [])
        print(f"✅ Found {len(trending)} trending articles")
        for i, article in enumerate(trending[:5], 1):
            print(f"   {i}. 🔥 {article.get('title', 'No title')}")
    else:
        print("❌ Failed to get trending news")
    
    print("\n🎉 News Viewing Complete!")

def show_how_ads_will_appear():
    """Show exactly how ads will appear with your news"""
    print("\n📢 **How Ads Will Appear With Your 9 News Articles**")
    print("=" * 60)
    
    print("\n**Current Ad Placement Rules:**")
    print("   📰 Position 1: News Article")
    print("   📰 Position 2: News Article") 
    print("   📰 Position 3: News Article")
    print("   📢 Position 4: ADVERTISEMENT")
    print("   📰 Position 5: News Article")
    print("   📰 Position 6: News Article")
    print("   📰 Position 7: News Article")
    print("   📢 Position 8: ADVERTISEMENT")
    print("   📰 Position 9: News Article")
    print("   📢 Position 10: ADVERTISEMENT (if more ads available)")
    
    print("\n**With Your 9 News Articles:**")
    print("   🟢 News: 9 articles (your existing content)")
    print("   🔴 Ads: 0-2 ads (depending on available ads)")
    print("   📊 Total: 9-11 items in feed")
    
    print("\n**Your News Articles in Order:**")
    your_articles = [
        "Local Festival Celebrates Cultural Heritage",
        "Cultural Festival This Weekend", 
        "University Research Breakthrough",
        "Traffic Updates: Major Road Construction",
        "New Hospital Opening Next Month",
        "Local Business Wins National Award",
        "Tech Company Launches Innovative AI Solutions",
        "Cricket Team Wins Championship Match",
        "Government Announces New Education Policy"
    ]
    
    for i, title in enumerate(your_articles, 1):
        ad_position = i + (i // 3)  # Add ad every 3 news items
        if i % 3 == 0 and i > 0:  # Every 3rd position
            print(f"   🔴 Position {i}: ADVERTISEMENT")
            print(f"   🟢 Position {i+1}: {title}")
        else:
            print(f"   🟢 Position {i}: {title}")

if __name__ == "__main__":
    view_existing_news()
    show_how_ads_will_appear()
