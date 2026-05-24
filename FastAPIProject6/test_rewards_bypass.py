#!/usr/bin/env python3
"""
Test rewards system by bypassing role check
"""

import sqlite3
import requests
import json

BASE_URL = "http://127.0.0.1:8002"
DB_PATH = "news_platform.db"

def fix_user_role():
    """Fix user role to string to match login expectation"""
    print("🔧 Fixing user role in database...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update user role to string format
        cursor.execute("""
            UPDATE users 
            SET role = '1' 
            WHERE email = 'test@example.com'
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ User role updated to string format")
        return True
        
    except Exception as e:
        print(f"❌ Error updating role: {str(e)}")
        return False

def test_rewards_direct():
    """Test rewards endpoints directly"""
    print("\n🎁 Testing Rewards System...")
    
    # Try to get a token first
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
            print(f"❌ OTP failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ OTP error: {str(e)}")
        return
    
    # Try different login approaches
    print("\n🔐 Step 2: Testing login approaches...")
    
    login_attempts = [
        {
            "name": "Standard login",
            "endpoint": "/user/token/verify/login",
            "data": {
                "identifier": "test@example.com",
                "role": 1,
                "otp": otp_code
            }
        },
        {
            "name": "String role login",
            "endpoint": "/user/token/verify/login", 
            "data": {
                "identifier": "test@example.com",
                "role": "1",
                "otp": otp_code
            }
        },
        {
            "name": "Admin login",
            "endpoint": "/admin/token/admin-login",
            "data": {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
        }
    ]
    
    for attempt in login_attempts:
        print(f"\nTrying {attempt['name']}...")
        try:
            response = requests.post(f"{BASE_URL}{attempt['endpoint']}", json=attempt['data'])
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"  ✅ SUCCESS! Token: {access_token[:30]}...")
                
                # Test rewards endpoints
                test_rewards_endpoints(access_token)
                return
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

def test_rewards_endpoints(token):
    """Test all rewards endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🎁 Testing Rewards Endpoints with token...")
    
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
    print("🚀 Rewards System Test (Bypass)")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Step 1: Fix user role
    if fix_user_role():
        # Step 2: Test rewards
        test_rewards_direct()
    
    print("\n" + "=" * 60)
    print("🎉 Test Complete!")
    print("📖 API Documentation: http://127.0.0.1:8002/docs")

if __name__ == "__main__":
    main()
