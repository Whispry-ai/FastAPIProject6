#!/usr/bin/env python3
"""
Script to view published news from your FastAPI application
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def get_published_news(user_uid="test_user", page=1, limit=10):
    """Get published news feed"""
    try:
        url = f"{BASE_URL}/news/feedz"
        params = {
            "user_uid": user_uid,
            "page": page,
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Failed to get news: {str(e)}")
        return None

def get_breaking_news():
    """Get breaking news"""
    try:
        url = f"{BASE_URL}/news/breaking"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Failed to get breaking news: {str(e)}")
        return None

def get_single_news(news_uid):
    """Get single news article"""
    try:
        url = f"{BASE_URL}/news/{news_uid}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Failed to get news: {str(e)}")
        return None

def search_news(query, category_id=None, state_id=None):
    """Search news"""
    try:
        url = f"{BASE_URL}/search/news"
        params = {"q": query}
        
        if category_id:
            params["category_id"] = category_id
        if state_id:
            params["state_id"] = state_id
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Failed to search news: {str(e)}")
        return None

def format_news_output(news_data, title="📰 Published News"):
    """Format news data for display"""
    print(f"\n{title}")
    print("=" * 60)
    
    if not news_data:
        print("❌ No news found")
        return
    
    if isinstance(news_data, dict) and "data" in news_data:
        news_list = news_data["data"]
    elif isinstance(news_data, list):
        news_list = news_data
    else:
        news_list = [news_data]
    
    for i, news in enumerate(news_list, 1):
        print(f"\n{i}. 📰 {news.get('title', 'No Title')}")
        print(f"   📝 {news.get('summary', 'No Summary')[:100]}...")
        print(f"   🆔 UID: {news.get('news_uid', 'N/A')}")
        print(f"   👁️ Views: {news.get('views_count', 0)}")
        print(f"   ❤️ Likes: {news.get('likes_count', 0)}")
        print(f"   💬 Comments: {news.get('comments_count', 0)}")
        print(f"   📤 Shares: {news.get('shares_count', 0)}")
        print(f"   📅 Created: {news.get('created_at', 'N/A')}")
        print(f"   🔗 Link: {BASE_URL}/news/{news.get('news_uid', '')}")
        print("-" * 60)

def main():
    """Main function to demonstrate news viewing"""
    print("🗞️  Hyperlocal News Viewer")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8001")
        return
    
    print("✅ Server is running!")
    
    # 1. Get published news feed
    print("\n📡 Fetching published news...")
    news_data = get_published_news()
    if news_data:
        format_news_output(news_data, "📰 Latest Published News")
    
    # 2. Get breaking news
    print("\n🚨 Fetching breaking news...")
    breaking_news = get_breaking_news()
    if breaking_news:
        format_news_output(breaking_news, "🚨 Breaking News")
    
    # 3. Search example
    print("\n🔍 Searching for 'politics' news...")
    search_results = search_news("politics")
    if search_results:
        format_news_output(search_results, "🔍 Search Results: Politics")
    
    # 4. Interactive menu
    while True:
        print("\n" + "=" * 60)
        print("📋 Options:")
        print("1. View latest news")
        print("2. View breaking news")
        print("3. Search news")
        print("4. Get specific news by UID")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            user_uid = input("Enter user UID (or press Enter for 'test_user'): ").strip() or "test_user"
            page = input("Enter page number (or press Enter for 1): ").strip()
            page = int(page) if page else 1
            
            news_data = get_published_news(user_uid, page)
            format_news_output(news_data, f"📰 Latest News (Page {page})")
            
        elif choice == "2":
            breaking_news = get_breaking_news()
            format_news_output(breaking_news, "🚨 Breaking News")
            
        elif choice == "3":
            query = input("Enter search term: ").strip()
            if query:
                search_results = search_news(query)
                format_news_output(search_results, f"🔍 Search Results: {query}")
            else:
                print("❌ Please enter a search term")
                
        elif choice == "4":
            news_uid = input("Enter news UID: ").strip()
            if news_uid:
                news_data = get_single_news(news_uid)
                if news_data:
                    format_news_output(news_data, f"📰 News Article: {news_uid}")
                else:
                    print(f"❌ News with UID '{news_uid}' not found")
            else:
                print("❌ Please enter a news UID")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
