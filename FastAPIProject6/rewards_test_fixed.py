#!/usr/bin/env python3
"""
Fixed rewards test - correct login endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_rewards_fixed():
    """Test rewards with correct login endpoint"""
    print("🎁 Rewards Test - Fixed")
    print("=" * 40)
    
    # Get token with correct endpoint
    token = get_token_correct()
    if not token:
        print("❌ Cannot get token")
        return
    
    # Test rewards endpoints
    test_endpoints(token)

def get_token_correct():
    """Get token using correct login endpoint"""
    print("🔐 Getting token (correct endpoint)...")
    
    try:
        # Send OTP
        otp_data = {"type": "email", "value": "test@example.com"}
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP: {otp_code}")
            
            # Login with CORRECT endpoint
            login_data = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            # Use correct endpoint: /user/token/verify/login
            response = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data, timeout=5)
            print(f"Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Token: {access_token[:30]}...")
                return access_token
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ OTP failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def test_endpoints(token):
    """Test rewards endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎁 Testing Rewards Endpoints:")
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet"),
        ("GET", "/rewards/referral/info", "🔗 Referral"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("POST", "/rewards/daily/login", "🎁 Daily")
    ]
    
    working = 0
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
            
            if response.status_code == 200:
                working += 1
                
        except Exception as e:
            print(f"❌ {name}: Error")
    
    print(f"\n📊 Results: {working}/{len(endpoints)} working")
    
    if working > 0:
        print("🎉 Rewards system is working!")
    else:
        print("❌ Rewards system needs attention")

def main():
    test_rewards_fixed()
    
    print("\n" + "=" * 40)
    print("💡 Fixed login endpoint: /user/token/verify/login")

if __name__ == "__main__":
    main()
