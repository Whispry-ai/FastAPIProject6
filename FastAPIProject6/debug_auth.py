#!/usr/bin/env python3
"""
Debug authentication issue
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def debug_authentication():
    """Debug authentication step by step"""
    print("🔍 Debug Authentication")
    print("=" * 40)
    
    # Step 1: Check server
    print("\n🌐 Step 1: Check server")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print("❌ Server not responding properly")
            return
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return
    
    # Step 2: Send OTP
    print("\n📱 Step 2: Send OTP")
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
            print(f"✅ OTP received: {otp_code}")
            
            # Step 3: Login
            print("\n🔐 Step 3: Login")
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
                print(f"✅ Token: {access_token[:50]}...")
                
                # Step 4: Test rewards
                test_rewards(access_token)
            else:
                print("❌ Login failed")
        else:
            print("❌ OTP failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_rewards(token):
    """Test rewards with token"""
    print("\n🎁 Step 4: Test Rewards")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test wallet
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet", headers=headers, timeout=5)
        print(f"Wallet: {response.status_code}")
        if response.status_code == 200:
            print("✅ Wallet working")
        else:
            print("❌ Wallet not working")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")

def main():
    debug_authentication()
    
    print("\n" + "=" * 40)
    print("💡 This will show exactly where authentication fails")

if __name__ == "__main__":
    main()
