#!/usr/bin/env python3
"""
Manual rewards system test - step by step
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def manual_rewards_test():
    """Manual step-by-step rewards test"""
    print("🎁 Manual Rewards System Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 40)
    
    # Step 1: Send OTP
    print("\n📱 Step 1: Send OTP")
    print("-" * 20)
    
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP Code: {otp_code}")
            
            # Step 2: Login
            print("\n🔐 Step 2: Login with OTP")
            print("-" * 20)
            
            login_data = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Access Token: {access_token[:50]}...")
                
                # Step 3: Test rewards
                print("\n🎁 Step 3: Test Rewards Endpoints")
                print("-" * 20)
                
                test_rewards_with_token(access_token)
            else:
                print("❌ Login failed")
        else:
            print("❌ OTP failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_rewards_with_token(token):
    """Test rewards endpoints with token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test wallet
    print("\n💰 Testing wallet...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test referral
    print("\n🔗 Testing referral...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Referral error: {str(e)}")
    
    # Test leaderboard
    print("\n🏆 Testing leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/rewards/leaderboard", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Leaderboard error: {str(e)}")
    
    # Test daily reward
    print("\n🎁 Testing daily reward...")
    try:
        response = requests.post(f"{BASE_URL}/rewards/daily/login", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Daily reward error: {str(e)}")

if __name__ == "__main__":
    manual_rewards_test()
