#!/usr/bin/env python3
"""
Simple user creation and login test
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def create_simple_user():
    """Create a simple test user directly"""
    print("👤 Creating test user...")
    
    # Try different user creation endpoints
    endpoints_to_try = [
        "/user_routes/create",
        "/users/create", 
        "/user/create",
        "/users/",
        "/user/register",
        "/register"
    ]
    
    user_data = {
        "phone": "+1234567890",
        "name": "Test User",
        "email": "test@example.com"
    }
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=user_data)
            print(f"Trying {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ User created successfully via {endpoint}!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
    
    return False

def test_login():
    """Test login with existing user"""
    print("\n🔐 Testing login...")
    
    login_data = {
        "identifier": "test@example.com",
        "role": 1,
        "otp": "123456"  # Default OTP
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/token/verify/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:30]}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_rewards(token):
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
        print(f"Wallet Balance: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test referral info
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers)
        print(f"Referral Info: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
    except Exception as e:
        print(f"❌ Referral error: {str(e)}")

def main():
    print("🚀 Simple User Creation & Rewards Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Try to create user
    if create_simple_user():
        # Step 2: Test login
        token = test_login()
        
        # Step 3: Test rewards
        test_rewards(token)
    
    print("\n" + "=" * 50)
    print("💡 If user creation failed, you may need to:")
    print("   1. Check existing users in database")
    print("   2. Use existing user credentials")
    print("   3. Check API documentation at http://127.0.0.1:8002/docs")

if __name__ == "__main__":
    main()
