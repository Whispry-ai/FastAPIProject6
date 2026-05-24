#!/usr/bin/env python3
"""
Quick rewards system test
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def quick_rewards_test():
    """Quick test of rewards system"""
    print("🎁 Quick Rewards System Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 40)
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Cannot get token")
        return
    
    # Test key endpoints
    test_key_endpoints(token)

def get_token():
    """Get authentication token"""
    print("🔐 Getting token...")
    
    try:
        # Send OTP
        otp_data = {"type": "email", "value": "test@example.com"}
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            
            # Login
            login_data = {"identifier": "test@example.com", "role": 5, "otp": otp_code}
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        
        print(f"❌ Token error: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        return None

def test_key_endpoints(token):
    """Test key rewards endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎁 Testing key endpoints:")
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet"),
        ("GET", "/rewards/referral/info", "🔗 Referral"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("POST", "/rewards/daily/login", "🎁 Daily Reward")
    ]
    
    working = 0
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code}")
            
            if response.status_code == 200:
                working += 1
                
        except Exception as e:
            print(f"❌ {description}: Error")
    
    print(f"\n📊 {working}/{len(endpoints)} endpoints working")
    
    if working > 0:
        print("🎉 Rewards system is working!")
    else:
        print("❌ Rewards system needs attention")

if __name__ == "__main__":
    quick_rewards_test()
