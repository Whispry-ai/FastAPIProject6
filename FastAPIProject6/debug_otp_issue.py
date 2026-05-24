#!/usr/bin/env python3
"""
Debug OTP verification 422 error
"""

import requests
import json

BASE_URL = "http://127.0.0.1:56613"

def debug_otp_verification():
    """Debug OTP verification 422 error"""
    print("🔍 Debug OTP Verification 422 Error")
    print("=" * 50)
    
    # Step 1: Send OTP
    print("\n📱 Step 1: Send OTP")
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
            
            # Step 2: Try different login endpoints
            print("\n🔐 Step 2: Test Login Endpoints")
            
            # Try endpoint 1: /user/token/verify/login
            print("\n🔍 Testing /user/token/verify/login...")
            login_data1 = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            try:
                response1 = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data1, timeout=5)
                print(f"Status: {response1.status_code}")
                print(f"Response: {response1.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Try endpoint 2: /user/auth/verify-otp
            print("\n🔍 Testing /user/auth/verify-otp...")
            login_data2 = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            try:
                response2 = requests.post(f"{BASE_URL}/user/auth/verify-otp", json=login_data2, timeout=5)
                print(f"Status: {response2.status_code}")
                print(f"Response: {response2.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Try endpoint 3: /admin/token/admin-login
            print("\n🔍 Testing /admin/token/admin-login...")
            login_data3 = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            try:
                response3 = requests.post(f"{BASE_URL}/admin/token/admin-login", json=login_data3, timeout=5)
                print(f"Status: {response3.status_code}")
                print(f"Response: {response3.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print(f"❌ OTP failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    debug_otp_verification()
    
    print("\n" + "=" * 50)
    print("💡 This will test all possible login endpoints")
    print("🌐 Server: http://127.0.0.1:56613")

if __name__ == "__main__":
    main()
