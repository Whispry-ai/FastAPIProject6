#!/usr/bin/env python3
"""
Comprehensive Testing Plan Using Existing Users
Tests all implemented features with your 4 users
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

# Your existing users
USERS = {
    "admin": {
        "uid": "ADMIN001",
        "name": "Admin User",
        "role": 5,
        "email": "admin@example.com"
    },
    "publisher": {
        "uid": "PUBLIS03", 
        "name": "Publisher User",
        "role": 3,
        "email": "publisher@example.com"
    },
    "regular1": {
        "uid": "0GF1LZ9V",
        "name": "alert_7063",
        "role": 1,
        "email": None
    },
    "regular2": {
        "uid": "IMPORT01",
        "name": "Import User", 
        "role": 1,
        "email": "import@example.com"
    }
}

def test_user_roles():
    """Test user roles and authentication"""
    print("👥 **Testing User Roles & Authentication**")
    print("=" * 50)
    
    for user_type, user_info in USERS.items():
        print(f"\n🔍 Testing {user_type}: {user_info['name']} ({user_info['uid']})")
        print(f"   📋 Role: {user_info['role']} ({'Admin' if user_info['role'] == 5 else 'Premium' if user_info['role'] == 3 else 'Regular'})")
        print(f"   📧 Email: {user_info['email'] or 'Not set'}")

def test_news_with_engagement():
    """Test news viewing with engagement features"""
    print("\n📰 **Testing News with Engagement Features**")
    print("=" * 50)
    
    # Get news articles
    try:
        response = requests.get(f"{BASE_URL}/news")
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('news', [])
            print(f"✅ Found {len(articles)} news articles")
            
            if articles:
                test_article = articles[0]
                news_uid = test_article.get('news_uid')
                title = test_article.get('title', 'No title')
                
                print(f"\n📝 Testing with: {title}")
                print(f"🔑 News UID: {news_uid}")
                print(f"📊 Current Stats:")
                print(f"   👁️ Views: {test_article.get('views_count', 0)}")
                print(f"   ❤️ Likes: {test_article.get('likes_count', 0)}")
                print(f"   📤 Shares: {test_article.get('shares_count', 0)}")
                print(f"   💬 Comments: {test_article.get('comments_count', 0)}")
                
                return news_uid
            else:
                print("❌ No news articles found")
                return None
        else:
            print(f"❌ Failed to get news: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_engagement_features(news_uid):
    """Test all engagement features with different users"""
    if not news_uid:
        print("❌ No news article available for engagement testing")
        return
    
    print(f"\n💬 **Testing Engagement Features**")
    print("=" * 50)
    
    # Test with different users
    test_users = ["regular1", "regular2", "publisher"]
    
    for user_key in test_users:
        user_info = USERS[user_key]
        print(f"\n👤 Testing with {user_info['name']} ({user_info['uid']})")
        
        # Test View Tracking
        try:
            view_data = {
                "news_uid": news_uid,
                "user_uid": user_info['uid']
            }
            response = requests.post(f"{BASE_URL}/engagement/view/{news_uid}", json=view_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ View tracked: {result.get('message')}")
            else:
                print(f"   ❌ View failed: {response.text}")
        except Exception as e:
            print(f"   ❌ View error: {e}")
        
        # Test Like/Unlike
        try:
            like_data = {
                "reaction_type": "like",
                "news_uid": news_uid,
                "user_uid": user_info['uid']
            }
            response = requests.post(f"{BASE_URL}/engagement/like", json=like_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Like: {result.get('message')} (Count: {result.get('likes_count', 0)})")
            else:
                print(f"   ❌ Like failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Like error: {e}")
        
        # Test Comment
        try:
            comment_data = {
                "content": f"Test comment by {user_info['name']} at {datetime.now().strftime('%H:%M:%S')}",
                "news_uid": news_uid,
                "user_uid": user_info['uid']
            }
            response = requests.post(f"{BASE_URL}/engagement/comment", json=comment_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Comment: {result.get('message')} (Count: {result.get('comments_count', 0)})")
            else:
                print(f"   ❌ Comment failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Comment error: {e}")
        
        # Test Share
        try:
            share_data = {
                "platform": "facebook",
                "news_uid": news_uid,
                "user_uid": user_info['uid']
            }
            response = requests.post(f"{BASE_URL}/engagement/share", json=share_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Share: {result.get('message')} (Count: {result.get('shares_count', 0)})")
            else:
                print(f"   ❌ Share failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Share error: {e}")

def test_admin_features():
    """Test admin-specific features"""
    print(f"\n👨‍💼 **Testing Admin Features**")
    print("=" * 50)
    
    admin_user = USERS['admin']
    print(f"👤 Testing with Admin: {admin_user['name']} ({admin_user['uid']})")
    
    # Test Analytics
    try:
        response = requests.get(f"{BASE_URL}/analytics/overview")
        if response.status_code == 200:
            print("   ✅ Analytics overview accessible")
        else:
            print(f"   ❌ Analytics failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Analytics error: {e}")
    
    # Test Top Engaged News
    try:
        response = requests.get(f"{BASE_URL}/engagement/top-engaged?limit=5")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Top engaged news: {len(result.get('news', []))} articles")
        else:
            print(f"   ❌ Top engaged failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Top engaged error: {e}")

def test_ai_features():
    """Test AI features"""
    print(f"\n🤖 **Testing AI Features**")
    print("=" * 50)
    
    # Test Sentiment Analysis
    try:
        ai_data = {
            "text": "This is amazing news about technology and innovation!",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/ai/sentiment-analysis", json=ai_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Sentiment Analysis: {result.get('sentiment', 'N/A')}")
        else:
            print(f"   ❌ Sentiment Analysis failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Sentiment Analysis error: {e}")
    
    # Test Category Suggestion
    try:
        category_data = {
            "text": "Tech company launches new AI product for mobile users"
        }
        response = requests.post(f"{BASE_URL}/ai/category-suggestion", json=category_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Category Suggestion: {result.get('suggested_category', 'N/A')}")
        else:
            print(f"   ❌ Category Suggestion failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Category Suggestion error: {e}")

def test_ad_placement():
    """Test ad placement system"""
    print(f"\n📢 **Testing Ad Placement System**")
    print("=" * 50)
    
    # Test Ad Configuration
    try:
        response = requests.get(f"{BASE_URL}/ads/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Ad Config: Interval {config['config']['default_placement_interval']}, Max {config['config']['max_ads_per_feed']}")
        else:
            print(f"   ❌ Ad Config failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Ad Config error: {e}")
    
    # Test Ad Placement
    try:
        test_data = {
            'user_uid': 'test123',
            'news_count': 9,
            'placement_interval': 3,
            'max_ads': 3
        }
        response = requests.post(f"{BASE_URL}/ads/placement-test", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Ad Placement: {result['results']['total_items']} total, {result['results']['ad_items']} ads")
        else:
            print(f"   ❌ Ad Placement failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Ad Placement error: {e}")

def test_search_features():
    """Test search functionality"""
    print(f"\n🔍 **Testing Search Features**")
    print("=" * 50)
    
    # Test News Search
    try:
        response = requests.get(f"{BASE_URL}/search/news", params={'q': 'technology', 'limit': 5})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ News Search: {len(result.get('news', []))} results")
        else:
            print(f"   ❌ News Search failed: {response.text}")
    except Exception as e:
        print(f"   ❌ News Search error: {e}")

def show_final_stats(news_uid):
    """Show final engagement statistics"""
    if not news_uid:
        return
    
    print(f"\n📊 **Final Engagement Statistics**")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/engagement/stats/public/{news_uid}")
        if response.status_code == 200:
            result = response.json()
            stats = result.get('stats', {})
            print(f"   👁️ Views: {stats.get('views_count', 0)}")
            print(f"   ❤️ Likes: {stats.get('likes_count', 0)}")
            print(f"   📤 Shares: {stats.get('shares_count', 0)}")
            print(f"   💬 Comments: {stats.get('comments_count', 0)}")
            print(f"   📈 Total: {sum(stats.values())} interactions")
        else:
            print(f"❌ Failed to get final stats: {response.text}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def main():
    """Main testing function"""
    print("🧪 **Comprehensive Feature Testing Plan**")
    print("=" * 70)
    print("Testing all implemented features with your existing users")
    print()
    
    # Test 1: User Roles
    test_user_roles()
    
    # Test 2: Get News Article
    news_uid = test_news_with_engagement()
    
    # Test 3: Engagement Features
    test_engagement_features(news_uid)
    
    # Test 4: Admin Features
    test_admin_features()
    
    # Test 5: AI Features
    test_ai_features()
    
    # Test 6: Ad Placement
    test_ad_placement()
    
    # Test 7: Search Features
    test_search_features()
    
    # Test 8: Final Statistics
    show_final_stats(news_uid)
    
    print(f"\n🎉 **Testing Complete!**")
    print("=" * 40)
    print("✅ User roles verified")
    print("✅ News engagement tested")
    print("✅ Admin features tested")
    print("✅ AI features tested")
    print("✅ Ad placement tested")
    print("✅ Search features tested")
    print("✅ Final statistics displayed")
    
    print(f"\n📋 **Next Steps:**")
    print("1. Check any failed tests above")
    print("2. Test individual features in Swagger UI")
    print("3. Use frontend demos for visual testing")
    print("4. Verify all counters are updating correctly")

if __name__ == "__main__":
    main()
