#!/usr/bin/env python3
"""
Check AI Endpoints Status
Verify all AI endpoints are accessible and working
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_ai_endpoints():
    """Check all AI endpoints"""
    print("🤖 **AI Endpoints Status Check**")
    print("=" * 60)
    
    if not check_server_status():
        print("❌ Server is not running. Start server first.")
        return
    
    # AI endpoints to check
    ai_endpoints = [
        {
            "name": "Sentiment Analysis",
            "path": "/ai/sentiment-analysis",
            "method": "POST",
            "description": "Analyze text sentiment with emotion detection"
        },
        {
            "name": "Fake News Detection", 
            "path": "/ai/fake-news-detection",
            "method": "POST",
            "description": "Detect fake news with credibility scoring"
        },
        {
            "name": "Category Suggestion",
            "path": "/ai/category-suggestion", 
            "method": "POST",
            "description": "Suggest categories for news content"
        },
        {
            "name": "Comprehensive Content Analysis",
            "path": "/ai/content-analysis",
            "method": "POST", 
            "description": "Complete AI analysis of content"
        },
        {
            "name": "CSV Batch Analysis",
            "path": "/ai/csv-analysis",
            "method": "POST",
            "description": "Batch process CSV files with AI analysis"
        },
        {
            "name": "CSV Template Download",
            "path": "/ai/csv-template",
            "method": "GET",
            "description": "Download CSV template for batch analysis"
        },
        {
            "name": "Supported Languages",
            "path": "/ai/supported-languages", 
            "method": "GET",
            "description": "Get list of supported AI languages"
        }
    ]
    
    print(f"📊 Checking {len(ai_endpoints)} AI endpoints...")
    
    results = []
    
    for endpoint in ai_endpoints:
        print(f"\n🔍 Checking: {endpoint['name']}")
        print(f"   Method: {endpoint['method']} {endpoint['path']}")
        print(f"   Description: {endpoint['description']}")
        
        try:
            url = f"{BASE_URL}{endpoint['path']}"
            
            if endpoint['method'] == 'GET':
                response = requests.get(url, timeout=10)
            else:
                # For POST endpoints, just check if they exist
                response = requests.post(url, json={}, timeout=10)
            
            status = "✅ Available" if response.status_code in [200, 422] else "❌ Error"
            results.append({
                "endpoint": endpoint['name'],
                "path": endpoint['path'],
                "method": endpoint['method'],
                "status_code": response.status_code,
                "status": status,
                "accessible": response.status_code in [200, 422]
            })
            
            print(f"   Status: {status} ({response.status_code})")
            
        except requests.exceptions.RequestException as e:
            print(f"   Status: ❌ Connection Error ({str(e)})")
            results.append({
                "endpoint": endpoint['name'],
                "path": endpoint['path'], 
                "method": endpoint['method'],
                "status_code": None,
                "status": "❌ Connection Error",
                "accessible": False,
                "error": str(e)
            })
        except Exception as e:
            print(f"   Status: ❌ Error ({str(e)})")
            results.append({
                "endpoint": endpoint['name'],
                "path": endpoint['path'],
                "method": endpoint['method'],
                "status_code": None,
                "status": "❌ Error", 
                "accessible": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n📋 **AI Endpoints Summary:**")
    print("=" * 60)
    
    accessible_count = sum(1 for r in results if r['accessible'])
    total_count = len(results)
    
    print(f"✅ Accessible: {accessible_count}/{total_count}")
    print(f"❌ Not Accessible: {total_count - accessible_count}/{total_count}")
    
    if accessible_count == total_count:
        print(f"\n🎉 All AI endpoints are accessible and working!")
    elif accessible_count > 0:
        print(f"\n⚠️  Some AI endpoints are accessible ({accessible_count}/{total_count})")
    else:
        print(f"\n❌ No AI endpoints are accessible")
    
    print(f"\n📊 **Detailed Results:**")
    for result in results:
        status_icon = "✅" if result['accessible'] else "❌"
        print(f"   {status_icon} {result['endpoint']}: {result['status']}")
        if not result['accessible'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    return results

def test_ai_functionality():
    """Test actual AI functionality with sample data"""
    print(f"\n🧪 **Testing AI Functionality**")
    print("=" * 60)
    
    # Test sentiment analysis
    print("\n🔍 Testing Sentiment Analysis...")
    try:
        sentiment_data = {
            "text": "This is a great day! I'm feeling very happy and excited about the news.",
            "language": "en"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/sentiment-analysis",
            json=sentiment_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sentiment Analysis Working:")
            print(f"   Sentiment: {result.get('data', {}).get('sentiment', 'N/A')}")
            print(f"   Confidence: {result.get('data', {}).get('confidence', 'N/A')}")
            emotions = result.get('data', {}).get('emotions', {})
            if emotions:
                print(f"   Emotions: {emotions}")
        else:
            print("❌ Sentiment Analysis Failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Sentiment Analysis Error: {str(e)}")
    
    # Test fake news detection
    print("\n🔍 Testing Fake News Detection...")
    try:
        fake_news_data = {
            "title": "Breaking: Scientists Discover Cure for Common Cold",
            "content": "Scientists claim to have found a revolutionary cure that eliminates all symptoms of the common cold overnight. The treatment involves a single injection that boosts the immune system permanently."
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/fake-news-detection",
            json=fake_news_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Fake News Detection Working:")
            print(f"   Analysis: {result.get('data', {}).get('analysis', 'N/A')}")
            print(f"   Confidence: {result.get('data', {}).get('confidence', 'N/A')}")
        else:
            print("❌ Fake News Detection Failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Fake News Detection Error: {str(e)}")
    
    # Test category suggestion
    print("\n🔍 Testing Category Suggestion...")
    try:
        category_data = {
            "text": "Local tech startup raises $10M in Series A funding round led by venture capitalists. The company plans to expand to three new cities and hire 50 engineers."
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/category-suggestion",
            json=category_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Category Suggestion Working:")
            categories = result.get('data', {}).get('categories', [])
            if categories:
                print(f"   Suggested Categories: {categories}")
            confidence = result.get('data', {}).get('confidence', 'N/A')
            print(f"   Confidence: {confidence}")
        else:
            print("❌ Category Suggestion Failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Category Suggestion Error: {str(e)}")

def main():
    """Main function"""
    print("🤖 **AI Endpoints Checker**")
    print("=" * 60)
    print("This script will check all AI endpoints and test their functionality.")
    print("Make sure the FastAPI server is running on http://localhost:8001")
    print()
    
    # Check endpoints
    results = check_ai_endpoints()
    
    # Ask user if they want to test functionality
    if any(r['accessible'] for r in results):
        choice = input(f"\n🧪 Test AI functionality? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            test_ai_functionality()
    
    print(f"\n📊 **Final Status Check completed at {datetime.now().isoformat()}**")

if __name__ == "__main__":
    main()
