#!/usr/bin/env python3
"""
Complete rewards system test script
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_rewards_system():
    """Complete test of rewards system"""
    print("🎁 Rewards System Complete Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Step 1: Authentication
    token = authenticate_user()
    if not token:
        print("❌ Authentication failed")
        return
    
    # Step 2: Test all rewards endpoints
    test_all_rewards_endpoints(token)
    
    # Step 3: Test rewards functionality
    test_rewards_functionality(token)

def authenticate_user():
    """Authenticate user and get token"""
    print("\n🔐 Step 1: Authentication")
    print("-" * 30)
    
    # Send OTP
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
            
            # Login
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
                return access_token
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ OTP failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
    
    return None

def test_all_rewards_endpoints(token):
    """Test all rewards endpoints"""
    print("\n🎁 Step 2: Test All Rewards Endpoints")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet Balance"),
        ("GET", "/rewards/referral/info", "🔗 Referral Info"),
        ("GET", "/rewards/referral/stats", "📊 Referral Stats"),
        ("POST", "/rewards/referral/claim", "🎁 Claim Referral"),
        ("POST", "/rewards/daily/login", "🎁 Daily Login"),
        ("GET", "/rewards/daily/status", "📅 Daily Status"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("GET", "/rewards/leaderboard/top", "🥇 Top Users"),
        ("GET", "/rewards/transactions/history", "📊 Transaction History"),
        ("GET", "/rewards/transactions/pending", "⏳ Pending Rewards"),
        ("POST", "/rewards/engagement/claim", "🎯 Engagement Reward"),
        ("GET", "/rewards/engagement/stats", "📈 Engagement Stats"),
        ("GET", "/rewards/streak/current", "🔥 Current Streak"),
        ("GET", "/rewards/streak/history", "📅 Streak History"),
        ("GET", "/rewards/coupons/available", "🎟 Available Coupons"),
        ("POST", "/rewards/coupons/redeem", "🎟 Redeem Coupon"),
        ("GET", "/rewards/coupons/history", "📄 Coupon History"),
        ("GET", "/rewards/stats/overview", "📊 Overview"),
        ("GET", "/rewards/stats/earnings", "💰 Earnings"),
        ("GET", "/rewards/stats/spending", "💸 Spending")
    ]
    
    working_count = 0
    total_count = len(endpoints)
    
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
            elif response.status_code == 500:
                print(f"❌ Server error")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")
    
    print(f"\n📊 Results: {working_count}/{total_count} endpoints working")
    
    if working_count == total_count:
        print("🎉 All rewards endpoints working!")
    elif working_count > 0:
        print("⚠️  Some rewards endpoints working")
    else:
        print("❌ No rewards endpoints working")

def test_rewards_functionality(token):
    """Test rewards functionality"""
    print("\n🎁 Step 3: Test Rewards Functionality")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Check wallet
    print("💰 Testing wallet...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet", headers=headers, timeout=5)
        if response.status_code == 200:
            wallet_data = response.json()
            print(f"✅ Wallet: {wallet_data}")
        else:
            print(f"❌ Wallet error: {response.status_code}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test 2: Claim daily reward
    print("\n🎁 Testing daily reward...")
    try:
        response = requests.post(f"{BASE_URL}/rewards/daily/login", headers=headers, timeout=5)
        if response.status_code == 200:
            reward_data = response.json()
            print(f"✅ Daily reward: {reward_data}")
        else:
            print(f"❌ Daily reward error: {response.status_code}")
    except Exception as e:
        print(f"❌ Daily reward error: {str(e)}")
    
    # Test 3: Check leaderboard
    print("\n🏆 Testing leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/leaderboard", headers=headers, timeout=5)
        if response.status_code == 200:
            leaderboard_data = response.json()
            print(f"✅ Leaderboard: {leaderboard_data}")
        else:
            print(f"❌ Leaderboard error: {response.status_code}")
    except Exception as e:
        print(f"❌ Leaderboard error: {str(e)}")
    
    # Test 4: Check referral info
    print("\n🔗 Testing referral info...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers, timeout=5)
        if response.status_code == 200:
            referral_data = response.json()
            print(f"✅ Referral info: {referral_data}")
        else:
            print(f"❌ Referral info error: {response.status_code}")
    except Exception as e:
        print(f"❌ Referral info error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Starting Rewards System Test")
    print("📋 Make sure server is running on port 8000")
    print("🌐 Server: http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("\nPress Enter to start testing...")
    input()
    
    test_rewards_system()
    
    print("\n" + "=" * 60)
    print("🎉 Rewards System Test Complete!")
    print("💡 Check results above for working endpoints")

if __name__ == "__main__":
    main()
