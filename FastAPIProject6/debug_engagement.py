#!/usr/bin/env python3
"""
Debug engagement endpoints step by step
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def debug_engagement():
    """Debug engagement endpoints systematically"""
    print("🔍 **Debugging Engagement Endpoints**")
    print("=" * 50)
    
    # Step 1: Check if server is running
    print("\n1. Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Step 2: Check available routes
    print(f"\n2. Checking available routes...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI error: {e}")
    
    # Step 3: Test basic news endpoint
    print(f"\n3. Testing basic news endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/news")
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('news', [])
            print(f"✅ News endpoint working: {len(articles)} articles")
            if articles:
                test_article = articles[0]
                news_uid = test_article.get('news_uid')
                print(f"   Test article UID: {news_uid}")
                return news_uid
        else:
            print(f"❌ News endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ News endpoint error: {e}")
    
    return None

def test_engagement_endpoints(news_uid):
    """Test engagement endpoints with a specific news UID"""
    if not news_uid:
        print("❌ No news UID available for testing")
        return
    
    print(f"\n4. Testing engagement endpoints...")
    
    # Test engagement stats (should work without auth)
    print(f"\n   4a. Testing engagement stats...")
    try:
        response = requests.get(f"{BASE_URL}/engagement/stats/public/{news_uid}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Stats working: {result}")
        else:
            print(f"   ❌ Stats failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test top engaged news
    print(f"\n   4b. Testing top engaged news...")
    try:
        response = requests.get(f"{BASE_URL}/engagement/top-engaged?limit=5")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Top engaged working: {len(result.get('news', []))} articles")
        else:
            print(f"   ❌ Top engaged failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Top engaged error: {e}")
    
    # Test like endpoint (may require auth)
    print(f"\n   4c. Testing like endpoint...")
    try:
        like_data = {
            "reaction_type": "like",
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/like", json=like_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Like working: {result}")
        else:
            print(f"   ❌ Like failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Like error: {e}")
    
    # Test view endpoint
    print(f"\n   4d. Testing view endpoint...")
    try:
        view_data = {
            "news_uid": news_uid,
            "user_uid": "test123"
        }
        response = requests.post(f"{BASE_URL}/engagement/view/{news_uid}", json=view_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ View working: {result}")
        else:
            print(f"   ❌ View failed: {response.text}")
    except Exception as e:
        print(f"   ❌ View error: {e}")

def check_server_logs():
    """Check if there are any server errors"""
    print(f"\n5. Checking for server issues...")
    print("   Look at your terminal where the server is running")
    print("   Check for any error messages or import issues")

if __name__ == "__main__":
    news_uid = debug_engagement()
    if news_uid:
        test_engagement_endpoints(news_uid)
    check_server_logs()
    
    print(f"\n🎯 **Debug Summary:**")
    print("   If engagement endpoints return 404, the routes aren't loaded")
    print("   If they return 500, there's a code error")
    print("   If they return 401/403, authentication is needed")
    print("   Check server terminal for detailed error messages")
