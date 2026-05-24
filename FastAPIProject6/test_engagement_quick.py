#!/usr/bin/env python3
"""
Quick test for likes, shares, and views functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_engagement_endpoints():
    """Test likes, shares, and views endpoints"""
    print("🧪 **Testing Likes, Shares, Views Endpoints**")
    print("=" * 50)
    
    # First get a news article
    print("\n1. Getting news article...")
    try:
        response = requests.get(f"{BASE_URL}/news")
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('news', [])
            
            if not articles:
                print("❌ No news articles found")
                return
            
            test_article = articles[0]
            news_uid = test_article.get('news_uid')
            title = test_article.get('title', 'No title')
            
            print(f"✅ Found article: {title}")
            print(f"🔑 News UID: {news_uid}")
            print(f"📊 Current stats:")
            print(f"   👁️ Views: {test_article.get('views_count', 0)}")
            print(f"   ❤️ Likes: {test_article.get('likes_count', 0)}")
            print(f"   📤 Shares: {test_article.get('shares_count', 0)}")
            print(f"   💬 Comments: {test_article.get('comments_count', 0)}")
            
        else:
            print(f"❌ Failed to get news: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting news: {e}")
        return
    
    # Test Views
    print(f"\n2. Testing View Tracking...")
    try:
        view_data = {
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/view/{news_uid}", json=view_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ View tracked: {result.get('message')}")
            print(f"   Views count: {result.get('views_count', 0)}")
        else:
            print(f"❌ View tracking failed: {response.text}")
    except Exception as e:
        print(f"❌ View tracking error: {e}")
    
    # Test Likes
    print(f"\n3. Testing Like/Unlike...")
    try:
        like_data = {
            "reaction_type": "like",
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/like", json=like_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Like action: {result.get('message')}")
            print(f"   Likes count: {result.get('likes_count', 0)}")
        else:
            print(f"❌ Like action failed: {response.text}")
    except Exception as e:
        print(f"❌ Like action error: {e}")
    
    # Test Shares
    print(f"\n4. Testing Share Tracking...")
    try:
        share_data = {
            "platform": "facebook",
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/share", json=share_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Share tracked: {result.get('message')}")
            print(f"   Shares count: {result.get('shares_count', 0)}")
        else:
            print(f"❌ Share tracking failed: {response.text}")
    except Exception as e:
        print(f"❌ Share tracking error: {e}")
    
    # Test Comments
    print(f"\n5. Testing Comments...")
    try:
        comment_data = {
            "content": "Test comment from quick test",
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/comment", json=comment_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comment added: {result.get('message')}")
            print(f"   Comments count: {result.get('comments_count', 0)}")
        else:
            print(f"❌ Comment failed: {response.text}")
    except Exception as e:
        print(f"❌ Comment error: {e}")
    
    # Get final stats
    print(f"\n6. Getting Final Stats...")
    try:
        response = requests.get(f"{BASE_URL}/engagement/stats/public/{news_uid}")
        if response.status_code == 200:
            result = response.json()
            stats = result.get('stats', {})
            print(f"✅ Final stats:")
            print(f"   👁️ Views: {stats.get('views_count', 0)}")
            print(f"   ❤️ Likes: {stats.get('likes_count', 0)}")
            print(f"   📤 Shares: {stats.get('shares_count', 0)}")
            print(f"   💬 Comments: {stats.get('comments_count', 0)}")
        else:
            print(f"❌ Failed to get stats: {response.text}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    print(f"\n🎉 **Test Complete!**")

if __name__ == "__main__":
    test_engagement_endpoints()
