#!/usr/bin/env python3
"""
Where to View Published News
Complete guide to accessing published news articles
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def show_news_viewing_methods():
    """Show different ways to view published news"""
    print("📰 **Where to View Published News**")
    print("=" * 60)
    
    print("\n🎯 **Available Methods to View News:**")
    print("-" * 50)
    
    methods = [
        {
            "method": "All Published News",
            "description": "Get all approved news articles",
            "endpoint": "GET /news",
            "auth": "Not required"
        },
        {
            "method": "News by Category",
            "description": "Get news filtered by category",
            "endpoint": "GET /news/categories",
            "auth": "Not required"
        },
        {
            "method": "Trending News",
            "description": "Get most popular/trending news",
            "endpoint": "GET /news/trending",
            "auth": "Not required"
        },
        {
            "method": "News by Location",
            "description": "Get news by state/district/city",
            "endpoint": "GET /location/states/{id}/news",
            "auth": "Not required"
        },
        {
            "method": "Search News",
            "description": "Search news with filters",
            "endpoint": "GET /search/news",
            "auth": "Not required"
        },
        {
            "method": "Recommended News",
            "description": "Get personalized recommendations",
            "endpoint": "GET /news/recommended",
            "auth": "Required"
        },
        {
            "method": "News by UID",
            "description": "Get specific news article",
            "endpoint": "GET /news/{news_uid}",
            "auth": "Not required"
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. **{method['method']}**")
        print(f"   📝 {method['description']}")
        print(f"   🔗 {method['endpoint']}")
        print(f"   🔐 Auth: {method['auth']}")

def show_news_endpoints():
    """Show all news-related endpoints"""
    print("\n📋 **Complete News Endpoints**")
    print("=" * 40)
    
    news_endpoints = [
        {
            "section": "Basic News",
            "endpoints": [
                ("GET /news", "All published news"),
                ("GET /news/{news_uid}", "Specific news article"),
                ("GET /news/categories", "All news categories")
            ]
        },
        {
            "section": "Enhanced News",
            "endpoints": [
                ("GET /news/trending", "Trending news articles"),
                ("GET /news/recommended", "Personalized recommendations"),
                ("GET /news/{news_uid}/report", "Report inappropriate news"),
                ("POST /news/{news_uid}/bookmark", "Bookmark news article"),
                ("DELETE /news/{news_uid}/unbookmark", "Remove bookmark")
            ]
        },
        {
            "section": "Search & Filter",
            "endpoints": [
                ("GET /search/news", "Advanced news search"),
                ("GET /search/suggestions", "Search suggestions")
            ]
        },
        {
            "section": "Location-Based News",
            "endpoints": [
                ("GET /location/states", "All states with news count"),
                ("GET /location/states/{id}/districts", "Districts in state"),
                ("GET /location/districts/{id}/cities", "Cities in district"),
                ("GET /location/search", "Search locations")
            ]
        }
    ]
    
    for section in news_endpoints:
        print(f"\n📍 {section['section']}:")
        for endpoint, description in section['endpoints']:
            auth = "🔒" if "recommended" in endpoint or "bookmark" in endpoint else "🌐"
            print(f"   {auth} {endpoint}")
            print(f"      📝 {description}")

def show_testing_examples():
    """Show practical examples for viewing news"""
    print("\n🧪 **Testing News Viewing**")
    print("=" * 40)
    
    print("\n**Example 1: Get All Published News**")
    print("```python")
    print("import requests")
    print()
    print("# Get all published news")
    print("response = requests.get('http://localhost:8001/news')")
    print("if response.status_code == 200:")
    print("    news_data = response.json()")
    print("    print(f\"Found {len(news_data['news'])} news articles\")")
    print("    for article in news_data['news'][:3]:")
    print("        print(f\"📰 {article['title']}\")")
    print("        print(f\"   👁️ Views: {article['views_count']}\")")
    print("        print(f\"   ❤️ Likes: {article['likes_count']}\")")
    print("```")
    
    print("\n**Example 2: Get News by Category**")
    print("```python")
    print("# Get news categories first")
    print("response = requests.get('http://localhost:8001/news/categories')")
    print("categories = response.json()['categories']")
    print()
    print("# Then get news for a specific category")
    print("category_id = categories[0]['id']  # First category")
    print("response = requests.get(")
    print("    f'http://localhost:8001/news?category_id={category_id}'")
    print(")")
    print("```")
    
    print("\n**Example 3: Search News**")
    print("```python")
    print("# Search for specific topics")
    print("response = requests.get(")
    print("    'http://localhost:8001/search/news',")
    print("    params={'q': 'technology', 'limit': 10}")
    print(")")
    print()
    print("search_results = response.json()['news']")
    print("for result in search_results:")
    print("    print(f\"🔍 {result['title']}\")")
    print("    print(f\"   📍 Location: {result.get('location', 'N/A')}\")")
    print("```")
    
    print("\n**Example 4: Get Trending News**")
    print("```python")
    print("# Get most popular news")
    print("response = requests.get('http://localhost:8001/news/trending')")
    print("trending = response.json()['news']")
    print()
    print("for i, article in enumerate(trending, 1):")
    print("    print(f\"{i}. 🔥 {article['title']}\")")
    print("       👁️ {article['views_count']} views")
    print("       ❤️ {article['likes_count']} likes")
    print("```")

def show_swagger_testing():
    """Show how to test news in Swagger UI"""
    print("\n🌐 **Testing News in Swagger UI**")
    print("=" * 40)
    
    print("\n**Step-by-Step:**")
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔍 Find 'News Enhanced' section")
    print("3. 🧪 Test different news endpoints")
    
    print("\n**Recommended Endpoints to Test:**")
    swagger_tests = [
        {
            "section": "News Enhanced",
            "endpoint": "GET /news/trending",
            "description": "View trending news",
            "auth": "Not required"
        },
        {
            "section": "News Enhanced",
            "endpoint": "GET /news/categories",
            "description": "Get all news categories",
            "auth": "Not required"
        },
        {
            "section": "Search",
            "endpoint": "GET /search/news",
            "description": "Search news articles",
            "auth": "Not required"
        },
        {
            "section": "Location Enhanced",
            "endpoint": "GET /location/states",
            "description": "Get states with news count",
            "auth": "Not required"
        }
    ]
    
    for test in swagger_tests:
        print(f"\n   📍 {test['section']}")
        print(f"      🔗 {test['endpoint']}")
        print(f"      📝 {test['description']}")
        print(f"      🔐 Auth: {test['auth']}")

def create_news_test_script():
    """Create a comprehensive news viewing script"""
    print("\n🚀 **Complete News Viewing Script**")
    print("=" * 40)
    
    script_content = '''
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def view_published_news():
    """Complete news viewing test"""
    print("📰 Viewing Published News...")
    
    # Test 1: Get All News
    print("\\n1. All Published News:")
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
    print("\\n2. News Categories:")
    response = requests.get(f"{BASE_URL}/news/categories")
    if response.status_code == 200:
        categories = response.json().get('categories', [])
        print(f"✅ Found {len(categories)} categories")
        for cat in categories[:5]:
            print(f"   📂 {cat.get('name', 'Unknown')}")
    else:
        print("❌ Failed to get categories")
    
    # Test 3: Get Trending News
    print("\\n3. Trending News:")
    response = requests.get(f"{BASE_URL}/news/trending")
    if response.status_code == 200:
        trending = response.json().get('news', [])
        print(f"✅ Found {len(trending)} trending articles")
        for i, article in enumerate(trending[:3], 1):
            print(f"   {i}. 🔥 {article.get('title', 'No title')[:50]}...")
    else:
        print("❌ Failed to get trending news")
    
    # Test 4: Search News
    print("\\n4. Search News:")
    response = requests.get(f"{BASE_URL}/search/news", params={'q': 'technology', 'limit': 5})
    if response.status_code == 200:
        search_results = response.json().get('news', [])
        print(f"✅ Found {len(search_results)} search results")
        for result in search_results:
            print(f"   🔍 {result.get('title', 'No title')[:50]}...")
    else:
        print("❌ Failed to search news")
    
    print("\\n🎉 News Viewing Test Complete!")

if __name__ == "__main__":
    view_published_news()
'''
    
    print("Create `view_news.py` with this content:")
    print("```python")
    print(script_content)
    print("```")
    print("Then run: python view_news.py")

def main():
    """Main function"""
    print("📰 **Complete Guide to Viewing Published News**")
    print("=" * 70)
    print("Here's how to access and view all published news articles.")
    print()
    
    show_news_viewing_methods()
    show_news_endpoints()
    show_testing_examples()
    show_swagger_testing()
    create_news_test_script()
    
    print(f"\n🎯 **Quick Start to View News:**")
    print("=" * 40)
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔍 Find 'News Enhanced' section")
    print("3. 🧪 Try 'GET /news' (all published news)")
    print("4. 🧪 Try 'GET /news/trending' (popular news)")
    print("5. 🧪 Try 'GET /news/categories' (browse categories)")
    print("6. 🔐 For personalized: Authorize and try 'GET /news/recommended'")
    
    print(f"\n💡 **What You'll See:**")
    print("=" * 30)
    print("📰 All published news articles")
    print("🔥 Trending and popular content")
    print("📂 News organized by categories")
    print("🔍 Search functionality")
    print("📍 Location-based news filtering")
    print("⭐ Personalized recommendations (with auth)")

if __name__ == "__main__":
    main()
