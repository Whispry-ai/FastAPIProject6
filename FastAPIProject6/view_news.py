#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def view_published_news():
    """Complete news viewing test"""
    print("📰 Viewing Published News...")
    
    # Test 1: Get All News
    print("\n1. All Published News:")
    response = requests.get(f"{BASE_URL}/news")
    if response.status_code == 200:
        news_data = response.json()
        print(f"✅ Found {len(news_data.get('news', []))} news articles")
        for i, article in enumerate(news_data.get('news', [])[:3], 1):
            print(f"   {i}. 📰 {article.get('title', 'No title')[:50]}...")
            print(f"      👁️ Views: {article.get('views_count', 0)}")
            print(f"      ❤️ Likes: {article.get('likes_count', 0)}")
    else:
        print("❌ Failed to get news")
    
    # Test 2: Get News Categories
    print("\n2. News Categories:")
    response = requests.get(f"{BASE_URL}/news/categories")
    if response.status_code == 200:
        categories = response.json().get('categories', [])
        print(f"✅ Found {len(categories)} categories")
        for cat in categories[:5]:
            print(f"   📂 {cat.get('name', 'Unknown')}")
    else:
        print("❌ Failed to get categories")
    
    # Test 3: Get Trending News
    print("\n3. Trending News:")
    response = requests.get(f"{BASE_URL}/news/trending")
    if response.status_code == 200:
        trending = response.json().get('news', [])
        print(f"✅ Found {len(trending)} trending articles")
        for i, article in enumerate(trending[:3], 1):
            print(f"   {i}. 🔥 {article.get('title', 'No title')[:50]}...")
    else:
        print("❌ Failed to get trending news")
    
    # Test 4: Search News
    print("\n4. Search News:")
    response = requests.get(f"{BASE_URL}/search/news", params={'q': 'technology', 'limit': 5})
    if response.status_code == 200:
        search_results = response.json().get('news', [])
        print(f"✅ Found {len(search_results)} search results")
        for result in search_results:
            print(f"   🔍 {result.get('title', 'No title')[:50]}...")
    else:
        print("❌ Failed to search news")
    
    print("\n🎉 News Viewing Test Complete!")

if __name__ == "__main__":
    view_published_news()
