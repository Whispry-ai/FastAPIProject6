#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8001"

def test_news_endpoint():
    """Simple test for news endpoint"""
    print("📰 Testing News Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/news", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ News endpoint working!")
            print(f"Response keys: {list(data.keys())}")
            
            if 'news' in data:
                articles = data['news']
                print(f"Found {len(articles)} articles")
                if articles:
                    article = articles[0]
                    print(f"First article: {article.get('title', 'No title')}")
                    print(f"News UID: {article.get('news_uid', 'No UID')}")
            else:
                print("No 'news' key in response")
                print(f"Response: {data}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_news_endpoint()
