#!/usr/bin/env python3
"""
Simple test of rewards endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_rewards_simple():
    """Test rewards endpoints with simple approach"""
    print("🎁 Testing Rewards System (Simple)")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Test 1: Send OTP
    print("\n📱 Step 1: Send OTP...")
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        print(f"OTP Send: {response.status_code}")
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP: {otp_code}")
            
            # Test 2: Login
            print("\n🔐 Step 2: Login...")
            login_data = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            print(f"Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Token: {access_token[:30]}...")
                
                # Test 3: Rewards endpoints
                test_rewards_endpoints(access_token)
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ OTP failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_rewards_endpoints(token):
    """Test key rewards endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Step 3: Testing Rewards Endpoints...")
    
    # Test key endpoints
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet"),
        ("GET", "/rewards/referral/info", "🔗 Referral"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("POST", "/rewards/daily/login", "🎁 Daily Reward")
    ]
    
    working_count = 0
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            print(f"{description}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Working")
                working_count += 1
            elif response.status_code == 401:
                print(f"❌ Not authenticated")
            elif response.status_code == 404:
                print(f"❌ Not found")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")
    
    print(f"\n📊 Results: {working_count}/{len(endpoints)} endpoints working")
    
    if working_count > 0:
        print("🎉 Rewards system is working!")
    else:
        print("❌ Rewards system needs attention")

def main():
    test_rewards_simple()
    
    print("\n" + "=" * 50)
    print("💡 If server is not running, start it with:")
    print("   python -m uvicorn main:app --port 8000")

if __name__ == "__main__":
    main()
