#!/usr/bin/env python3
"""
Test script for engagement social features (likes, shares, views, comments)
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    """Get authentication token"""
    try:
        # Send OTP
        otp_data = {"type": "email", "value": "test@example.com"}
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            
            # Login
            login_data = {"identifier": "test@example.com", "role": 5, "otp": otp_code}
            response = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        
        return None
        
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        return None

def get_news_uid(token):
    """Get a news UID from the database"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/news/all", headers=headers, timeout=5)
        if response.status_code == 200:
            news_list = response.json()
            if news_list and len(news_list) > 0:
                return news_list[0].get('news_uid')
        return None
    except Exception as e:
        print(f"❌ Error getting news: {str(e)}")
        return None

def test_engagement_features():
    """Test all engagement social features"""
    print("🧪 Testing Engagement Social Features")
    print("=" * 50)
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Cannot get token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    user_uid = "test_user_123"  # Replace with actual user UID if needed
    
    # Get a news UID
    news_uid = get_news_uid(token)
    if not news_uid:
        print("❌ Cannot get news UID - creating test news first")
        # Try to create a test news item
        try:
            news_data = {
                "title": "Test News for Engagement",
                "summary": "This is a test news item for engagement features",
                "language_id": 1,
                "city_id": 1
            }
            response = requests.post(f"{BASE_URL}/news/create", headers=headers, json=news_data, timeout=5)
            if response.status_code == 200:
                news = response.json()
                news_uid = news.get('news_uid')
                print(f"✅ Created test news with UID: {news_uid}")
            else:
                print(f"❌ Failed to create test news: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error creating test news: {str(e)}")
            return
    
    print(f"\n📰 Using news UID: {news_uid}")
    
    # Test 1: Create Reaction (Like)
    print("\n👍 Test 1: Create Reaction (Like)")
    try:
        reaction_data = {
            "news_uid": news_uid,
            "reaction_type": 1  # 1 = like
        }
        response = requests.post(
            f"{BASE_URL}/engagement/social/reactions?user_uid={user_uid}",
            headers=headers,
            json=reaction_data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Reaction created: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Reaction error: {str(e)}")
    
    # Test 2: Get News Reactions
    print("\n👍 Test 2: Get News Reactions")
    try:
        response = requests.get(
            f"{BASE_URL}/engagement/social/reactions/{news_uid}",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Reactions: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Get reactions error: {str(e)}")
    
    # Test 3: Create Comment
    print("\n💬 Test 3: Create Comment")
    try:
        comment_data = {
            "news_uid": news_uid,
            "comment_text": "This is a test comment!"
        }
        response = requests.post(
            f"{BASE_URL}/engagement/social/comments?user_uid={user_uid}",
            headers=headers,
            json=comment_data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Comment created: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Comment error: {str(e)}")
    
    # Test 4: Get News Comments
    print("\n💬 Test 4: Get News Comments")
    try:
        response = requests.get(
            f"{BASE_URL}/engagement/social/comments/{news_uid}",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Comments: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Get comments error: {str(e)}")
    
    # Test 5: Create Share
    print("\n📤 Test 5: Create Share")
    try:
        share_data = {
            "news_uid": news_uid,
            "platform": "whatsapp"
        }
        response = requests.post(
            f"{BASE_URL}/engagement/social/shares?user_uid={user_uid}",
            headers=headers,
            json=share_data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Share created: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Share error: {str(e)}")
    
    # Test 6: Get News Shares
    print("\n📤 Test 6: Get News Shares")
    try:
        response = requests.get(
            f"{BASE_URL}/engagement/social/shares/{news_uid}",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Shares: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Get shares error: {str(e)}")
    
    # Test 7: Create View
    print("\n👁️ Test 7: Create View")
    try:
        view_data = {
            "news_uid": news_uid
        }
        response = requests.post(
            f"{BASE_URL}/engagement/social/views?user_uid={user_uid}",
            headers=headers,
            json=view_data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ View created: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ View error: {str(e)}")
    
    # Test 8: Get Engagement Stats
    print("\n📊 Test 8: Get Engagement Stats")
    try:
        response = requests.get(
            f"{BASE_URL}/engagement/social/stats/{news_uid}?user_uid={user_uid}",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Engagement Stats: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Get stats error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Engagement Social Features Test Complete")

if __name__ == "__main__":
    test_engagement_features()
