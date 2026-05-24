#!/usr/bin/env python3
"""
Complete test of all rewards endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_fresh_token():
    """Get fresh authentication token"""
    print("🔐 Getting fresh authentication token...")
    
    # Send OTP for test@example.com
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data)
        print(f"OTP Send: {response.status_code}")
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP received: {otp_code}")
            
            # Login with OTP
            login_data = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data)
            print(f"Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Login successful! Token: {access_token[:30]}...")
                return access_token
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ OTP send failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting token: {str(e)}")
    
    return None

def test_all_rewards_endpoints(token):
    """Test all rewards endpoints"""
    if not token:
        print("❌ No token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Testing All Rewards Endpoints...")
    print("=" * 60)
    
    # List of all rewards endpoints to test
    endpoints_to_test = [
        ("GET", "/rewards/wallet", "💰 Wallet Balance"),
        ("GET", "/rewards/referral/info", "🔗 Referral Info"),
        ("GET", "/rewards/referral/stats", "📊 Referral Stats"),
        ("POST", "/rewards/referral/claim", "🎁 Claim Referral Reward"),
        ("POST", "/rewards/daily/login", "🎁 Daily Login Reward"),
        ("GET", "/rewards/daily/status", "📅 Daily Status"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("GET", "/rewards/leaderboard/top", "🥇 Top Users"),
        ("GET", "/rewards/transactions/history", "📊 Transaction History"),
        ("GET", "/rewards/transactions/pending", "⏳ Pending Rewards"),
        ("POST", "/rewards/engagement/claim", "🎯 Claim Engagement Reward"),
        ("GET", "/rewards/engagement/stats", "📈 Engagement Stats"),
        ("GET", "/rewards/streak/current", "🔥 Current Streak"),
        ("GET", "/rewards/streak/history", "📅 Streak History"),
        ("GET", "/rewards/coupons/available", "🎟 Available Coupons"),
        ("POST", "/rewards/coupons/redeem", "🎟 Redeem Coupon"),
        ("GET", "/rewards/coupons/history", "📄 Coupon History"),
        ("GET", "/rewards/stats/overview", "📊 Rewards Overview"),
        ("GET", "/rewards/stats/earnings", "💰 Earnings Stats"),
        ("GET", "/rewards/stats/spending", "💸 Spending Stats")
    ]
    
    success_count = 0
    total_count = len(endpoints_to_test)
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"{description}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {response.json()}")
                success_count += 1
            elif response.status_code == 401:
                print(f"❌ Not authenticated")
            elif response.status_code == 404:
                print(f"❌ Endpoint not found")
            elif response.status_code == 500:
                print(f"❌ Server error")
            else:
                print(f"❌ {response.text}")
                
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All rewards endpoints are working!")
    elif success_count > 0:
        print("⚠️  Some rewards endpoints are working")
    else:
        print("❌ No rewards endpoints are working")

def main():
    print("🚀 Complete Rewards System Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Get fresh token
    token = get_fresh_token()
    
    if token:
        # Test all rewards endpoints
        test_all_rewards_endpoints(token)
    else:
        print("❌ Failed to get authentication token")
    
    print("\n" + "=" * 60)
    print("💡 This test covers all rewards system functionality:")
    print("   - Wallet management")
    print("   - Referral system") 
    print("   - Daily rewards")
    print("   - Leaderboard")
    print("   - Transaction history")
    print("   - Coupon system")
    print("   - Engagement rewards")
    print("   - Streak tracking")
    print("   - Statistics")

if __name__ == "__main__":
    main()
