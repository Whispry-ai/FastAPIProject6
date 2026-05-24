#!/usr/bin/env python3
"""
Test the rewards system endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def create_user_and_login():
    """Create a test user and get token"""
    print("👤 Creating test user...")
    
    # Create user
    user_data = {
        "phone": "+1234567890",
        "name": "Test User",
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/create", json=user_data)
        if response.status_code == 200:
            print("✅ User created successfully!")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return None
    
    # Send OTP
    print("\n📱 Sending OTP...")
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/send-otp", json=otp_data)
        if response.status_code == 200:
            print("✅ OTP sent successfully!")
        else:
            print(f"❌ OTP sending failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error sending OTP: {str(e)}")
        return None
    
    # Login with OTP
    print("\n🔐 Logging in...")
    login_data = {
        "identifier": "test@example.com",
        "role": 1,
        "otp": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/token/verify/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful!")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def test_rewards_endpoints(token):
    """Test rewards endpoints"""
    if not token:
        print("❌ No token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Testing Rewards Endpoints...")
    
    # Test wallet balance
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet/balance", headers=headers)
        print(f"💰 Wallet Balance: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test referral info
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers)
        print(f"🔗 Referral Info: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Referral error: {str(e)}")
    
    # Test daily rewards
    try:
        response = requests.post(f"{BASE_URL}/rewards/daily/login", headers=headers)
        print(f"🎁 Daily Login Reward: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Daily reward error: {str(e)}")
    
    # Test referral reward
    try:
        response = requests.post(f"{BASE_URL}/rewards/referral/claim", headers=headers)
        print(f"🎁 Referral Claim: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Referral claim error: {str(e)}")

def main():
    print("🚀 Testing Rewards System")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Get token
    token = create_user_and_login()
    
    # Step 2: Test rewards
    test_rewards_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🎉 Rewards System Test Complete!")
    print(f"📖 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
