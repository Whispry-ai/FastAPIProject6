#!/usr/bin/env python3
"""
Test AI features for the Hyperlocal News Application
"""

import requests
import json

def test_ai_features():
    """Test all AI endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧠 Testing AI Features")
    print("=" * 50)
    
    # Test 1: Category Suggestion
    print("\n1. 🏷️  Testing Category Suggestion")
    try:
        response = requests.post(f"{base_url}/ai/suggest-category", json={
            "title": "Local election results announced",
            "content": "The city council has announced the results for yesterday's election with the winning party taking majority seats."
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Category: {data.get('suggested_category', 'Unknown')}")
            print(f"📊 Confidence: {data.get('confidence', 0):.2f}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Sentiment Analysis
    print("\n2. 😊 Testing Sentiment Analysis")
    try:
        response = requests.post(f"{base_url}/ai/analyze-sentiment", json={
            "text": "This is absolutely wonderful news! Our community is thriving with amazing developments."
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sentiment: {data.get('sentiment', 'Unknown')}")
            print(f"📈 Score: {data.get('score', 0):.3f}")
            print(f"💪 Positive words: {data.get('positive_words_count', 0)}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Fake News Detection
    print("\n3. 🔍 Testing Fake News Detection")
    try:
        response = requests.post(f"{base_url}/ai/detect-fake-news", json={
            "title": "SHOCKING! You won't believe what happened in our city last night!",
            "content": "BREAKING NEWS: This incredible miracle will change everything forever! Click here for the amazing secret!"
        })
        if response.status_code == 200:
            data = response.json()
            print(f"⚠️  Risk Level: {data.get('risk_level', 'Unknown')}")
            print(f"🚨 Warnings: {len(data.get('warnings', []))}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Comprehensive Analysis
    print("\n4. 📊 Testing Comprehensive Analysis")
    try:
        response = requests.post(f"{base_url}/ai/comprehensive-analysis", json={
            "title": "New technology park opens in downtown area",
            "content": "The city inaugurated a new technology park bringing hundreds of jobs to local residents."
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Category: {data.get('category', {}).get('suggested_category', 'Unknown')}")
            print(f"😊 Sentiment: {data.get('sentiment', {}).get('sentiment', 'Unknown')}")
            print(f"⚠️  Fake News Risk: {data.get('fake_news', {}).get('risk_level', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎯 AI Features Test Complete!")
    print("💡 Make sure your FastAPI app is running on port 8001")

if __name__ == "__main__":
    test_ai_features()
