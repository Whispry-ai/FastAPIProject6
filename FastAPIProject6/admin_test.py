#!/usr/bin/env python3
import requests
import json

# Replace with your admin token from Swagger UI
ADMIN_TOKEN = "YOUR_ADMIN_TOKEN"  # <-- Get from http://localhost:8001/docs
BASE_URL = "http://localhost:8001"

def test_admin_access():
    """Test admin access to all endpoints"""
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}
    
    print("👨‍💼 Testing Admin Access...")
    
    # Test 1: Check admin role
    print("\n1. Checking Admin Role:")
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Your role: {profile.get('role')} (Should be 5 for admin)")
    else:
        print("❌ Error getting profile")
        return
    
    # Test 2: AI Features
    print("\n2. Testing AI Features:")
    
    # Sentiment Analysis
    response = requests.post(
        f"{BASE_URL}/ai/sentiment-analysis",
        headers=headers,
        json={'text': 'This is fantastic news about technology!', 'language': 'en'}
    )
    if response.status_code == 200:
        print("✅ AI Sentiment Analysis Working")
        print(f"   Result: {response.json()}")
    else:
        print("❌ AI Sentiment Analysis Failed")
    
    # Fake News Detection
    response = requests.post(
        f"{BASE_URL}/ai/fake-news-detection",
        headers=headers,
        json={'title': 'Breaking News', 'content': 'Scientists discover amazing new technology'}
    )
    if response.status_code == 200:
        print("✅ AI Fake News Detection Working")
    else:
        print("❌ AI Fake News Detection Failed")
    
    # Category Suggestion
    response = requests.post(
        f"{BASE_URL}/ai/category-suggestion",
        headers=headers,
        json={'text': 'Tech company launches new AI product for mobile users'}
    )
    if response.status_code == 200:
        print("✅ AI Category Suggestion Working")
    else:
        print("❌ AI Category Suggestion Failed")
    
    # Test 3: Analytics
    print("\n3. Testing Analytics:")
    response = requests.get(f"{BASE_URL}/analytics/overview", headers=headers)
    if response.status_code == 200:
        print("✅ Analytics Dashboard Working")
    else:
        print("❌ Analytics Dashboard Failed")
    
    # Test 4: User Management
    print("\n4. Testing User Management:")
    response = requests.get(f"{BASE_URL}/user/stats", headers=headers)
    if response.status_code == 200:
        print("✅ User Statistics Working")
    else:
        print("❌ User Statistics Failed")
    
    # Test 5: Advertisement System
    print("\n5. Testing Advertisement System:")
    response = requests.get(f"{BASE_URL}/ads/config", headers=headers)
    if response.status_code == 200:
        print("✅ Ad Configuration Working")
    else:
        print("❌ Ad Configuration Failed")
    
    # Test 6: Enhanced News Features
    print("\n6. Testing Enhanced News Features:")
    response = requests.get(f"{BASE_URL}/news/categories", headers=headers)
    if response.status_code == 200:
        print("✅ News Categories Working")
    else:
        print("❌ News Categories Failed")
    
    print("\n🎉 Admin Access Test Complete!")

if __name__ == "__main__":
    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN":
        print("❌ Please replace YOUR_ADMIN_TOKEN with your actual admin token")
        print("🔐 Get your admin token from: http://localhost:8001/docs")
        print("\n📋 Steps to get token:")
        print("1. Go to http://localhost:8001/docs")
        print("2. Click 'Authorize' button")
        print("3. Complete Google login")
        print("4. Click 'Authorize' again in the dialog")
        print("5. Your token will be shown - copy it")
    else:
        test_admin_access()
