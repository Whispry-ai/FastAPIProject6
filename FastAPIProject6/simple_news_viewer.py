#!/usr/bin/env python3
"""
Simple script to view published news
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def get_news_feed():
    """Get published news feed"""
    try:
        response = requests.get(f"{BASE_URL}/news/feedz?user_uid=test_user")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def get_breaking_news():
    """Get breaking news"""
    try:
        response = requests.get(f"{BASE_URL}/news/breaking")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def display_news(news_data, title="📰 News"):
    print(f"\n{title}")
    print("=" * 50)
    
    if not news_data:
        print("No news found")
        return
    
    if isinstance(news_data, dict) and "data" in news_data:
        news_list = news_data["data"]
    elif isinstance(news_data, list):
        news_list = news_data
    else:
        news_list = [news_data]
    
    for i, news in enumerate(news_list[:5], 1):  # Show first 5
        print(f"\n{i}. {news.get('title', 'No Title')}")
        print(f"   📝 {news.get('summary', 'No Summary')[:80]}...")
        print(f"   👁️ Views: {news.get('views_count', 0)}")
        print(f"   ❤️ Likes: {news.get('likes_count', 0)}")
        print(f"   🆔 UID: {news.get('news_uid', 'N/A')}")

if __name__ == "__main__":
    print("🗞️  Hyperlocal News Viewer")
    print("=" * 50)
    
    # Test connection
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server not responding")
            exit()
    except:
        print("❌ Cannot connect to server")
        print("Make sure server is running on http://localhost:8001")
        exit()
    
    # Get news
    print("\n📡 Fetching news...")
    news = get_news_feed()
    if news:
        display_news(news, "📰 Latest News")
    
    # Get breaking news
    print("\n🚨 Fetching breaking news...")
    breaking = get_breaking_news()
    if breaking:
        display_news(breaking, "🚨 Breaking News")
    
    print("\n✅ Done! For more options, visit: http://localhost:8001/docs")
