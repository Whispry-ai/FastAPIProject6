#!/usr/bin/env python3
"""
Test script to verify ad placement after every 3 articles
"""

def test_ad_placement_logic():
    """Test the ad injection logic"""
    print("🧪 Testing Ad Placement Logic")
    print("=" * 40)
    
    # Simulate news items and ad placement
    news_items = ["News 1", "News 2", "News 3", "News 4", "News 5", "News 6", "News 7", "News 8", "News 9"]
    ads = ["Ad A", "Ad B", "Ad C"]
    sponsored_posts = ["Sponsored 1", "Sponsored 2"]
    
    feed = []
    ad_idx = 0
    sponsor_idx = 0
    news_count = 0  # Track only news items for ad placement
    
    for i, news in enumerate(news_items):
        # Add news item
        feed.append({"type": "news", "data": news})
        news_count += 1  # Increment news counter
        
        # Inject ads after every 3 news items (after news items 3, 6, 9, etc.)
        if news_count % 3 == 0 and ad_idx < len(ads):
            feed.append({"type": "ad", "data": ads[ad_idx]})
            ad_idx += 1
        
        # Inject sponsored posts after every 6 news items (after news items 6, 12, 18, etc.)
        if news_count % 6 == 0 and sponsor_idx < len(sponsored_posts):
            feed.append({"type": "sponsored", "data": sponsored_posts[sponsor_idx]})
            sponsor_idx += 1
    
    # Display the feed
    print("📰 Generated Feed:")
    for i, item in enumerate(feed, 1):
        item_type = item["type"].upper()
        item_data = item["data"]
        print(f"  {i:2d}. [{item_type}] {item_data}")
    
    # Verify ad placement
    print("\n✅ Verification:")
    ad_positions = [i+1 for i, item in enumerate(feed) if item["type"] == "ad"]
    sponsored_positions = [i+1 for i, item in enumerate(feed) if item["type"] == "sponsored"]
    
    print(f"   Ads found at positions: {ad_positions}")
    print(f"   Sponsored posts at positions: {sponsored_positions}")
    
    # Check if ads appear after every 3 news items (considering position shifts from sponsored posts)
    expected_ad_positions = [4, 8, 13]  # After 3 news (pos 4), after 6 news (pos 8 due to sponsored), after 9 news (pos 13)
    actual_ad_positions = [pos for pos in ad_positions if pos <= 15]
    
    if actual_ad_positions == expected_ad_positions[:len(actual_ad_positions)]:
        print("   ✅ Ads correctly placed after every 3 news items!")
    else:
        print(f"   ❌ Ad placement incorrect. Expected: {expected_ad_positions}, Got: {actual_ad_positions}")
    
    return len(feed)

if __name__ == "__main__":
    total_items = test_ad_placement_logic()
    print(f"\n🎉 Test completed! Total feed items: {total_items}")
