#!/usr/bin/env python3
"""
Simple Server Check
"""

import requests

def check_server():
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        print(f"✅ Server Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on port 8001")
        print("🔧 To start server:")
        print("   python -m uvicorn main:app --port 8001 --host 0.0.0.0 --reload")
        return False
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return False

def test_endpoints():
    if not check_server():
        return
    
    print("\n🌐 **Working URLs:**")
    print("   http://localhost:8001/ai_analysis_client.html")
    print("   http://localhost:8001/ad_placement_client.html")
    print("   http://localhost:8001/news_sharing_demo.html")
    print("   http://localhost:8001/docs")
    
    print("\n🤖 **AI Endpoints:**")
    print("   POST http://localhost:8001/ai/sentiment-analysis")
    print("   POST http://localhost:8001/ai/category-suggestion")
    print("   POST http://localhost:8001/ai/fake-news-detection")
    print("   GET  http://localhost:8001/ai/supported-languages")
    print("   GET  http://localhost:8001/ai/csv-template")

if __name__ == "__main__":
    test_endpoints()
