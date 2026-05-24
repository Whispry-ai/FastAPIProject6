#!/usr/bin/env python3
"""
Final test for admin login and rewards system
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_admin_login():
    """Test admin login with different approaches"""
    print("🚀 Testing Admin Login Approaches")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Send OTP first
    print("\n📱 Step 1: Sending OTP...")
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
            print(f"✅ OTP: {otp_code}")
        else:
            print(f"❌ OTP send failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ OTP send error: {str(e)}")
        return
    
    # Try different login approaches
    print("\n🔐 Step 2: Testing different login approaches...")
    
    login_attempts = [
        {
            "name": "Standard User Login",
            "endpoint": "/user/token/verify/login",
            "data": {
                "identifier": "test@example.com",
                "role": 1,  # USER role
                "otp": otp_code
            }
        },
        {
            "name": "Admin Login (Standard)",
            "endpoint": "/user/token/verify/login",
            "data": {
                "identifier": "test@example.com",
                "role": 5,  # ADMIN role
                "otp": otp_code
            }
        },
        {
            "name": "Admin Login (Admin Endpoint)",
            "endpoint": "/admin/token/admin-login",
            "data": {
                "identifier": "test@example.com",
                "role": 5,  # ADMIN role
                "otp": otp_code
            }
        }
    ]
    
    for attempt in login_attempts:
        print(f"\n🔐 Trying {attempt['name']}...")
        try:
            response = requests.post(f"{BASE_URL}{attempt['endpoint']}", json=attempt['data'])
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"  ✅ SUCCESS! Token: {access_token[:30]}...")
                
                # Test rewards with this token
                test_rewards_endpoints(access_token)
                return True
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    return False

def test_rewards_endpoints(token):
    """Test rewards endpoints with valid token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🎁 Testing Rewards Endpoints...")
    
    endpoints_to_test = [
        ("GET", "/rewards/wallet", "💰 Wallet Balance"),
        ("GET", "/rewards/referral/info", "🔗 Referral Info"),
        ("POST", "/rewards/daily/login", "🎁 Daily Login Reward"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("GET", "/rewards/transactions/history", "📊 Transaction History"),
        ("POST", "/rewards/referral/claim", "🎁 Claim Referral Reward")
    ]
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"{description}: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {response.json()}")
            elif response.status_code == 401:
                print(f"❌ Not authenticated")
            else:
                print(f"❌ {response.text}")
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")

def main():
    success = test_admin_login()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Admin Login & Rewards System Working!")
    else:
        print("❌ Admin Login Failed - Check role configuration")
    
    print("📖 API Documentation: http://127.0.0.1:8002/docs")
    print("💡 If login fails, check:")
    print("   1. User role in database")
    print("   2. Role comparison in login endpoint")
    print("   3. UserRole enum values")

if __name__ == "__main__":
    main()
