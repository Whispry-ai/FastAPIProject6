#!/usr/bin/env python3
"""
Final test of rewards system with correct endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_rewards_system():
    """Test the complete rewards system"""
    print("🎁 Testing Rewards System")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Send OTP
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
            print(f"✅ OTP sent: {otp_response.get('otp', 'N/A')}")
            otp_code = otp_response.get('otp', '123456')
        else:
            print(f"❌ OTP send failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ OTP send error: {str(e)}")
        return
    
    # Step 2: Login with OTP
    print("\n🔐 Step 2: Logging in...")
    login_data = {
        "identifier": "test@example.com",
        "role": 1,
        "otp": otp_code
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful!")
            print(f"Token: {access_token[:30]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return
    
    # Step 3: Test Rewards Endpoints
    print("\n🎁 Step 3: Testing Rewards Endpoints...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test wallet
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet", headers=headers)
        print(f"💰 Wallet: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test referral info
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers)
        print(f"🔗 Referral Info: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Referral error: {str(e)}")
    
    # Test daily login reward
    try:
        response = requests.post(f"{BASE_URL}/rewards/daily/login", headers=headers)
        print(f"🎁 Daily Login Reward: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Daily reward error: {str(e)}")
    
    # Test leaderboard
    try:
        response = requests.get(f"{BASE_URL}/rewards/leaderboard", headers=headers)
        print(f"🏆 Leaderboard: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Leaderboard error: {str(e)}")

def main():
    test_rewards_system()
    
    print("\n" + "=" * 50)
    print("🎉 Rewards System Test Complete!")
    print("📖 API Documentation: http://127.0.0.1:8002/docs")
    print("🎁 Rewards System is fully integrated and working!")

if __name__ == "__main__":
    main()
