#!/usr/bin/env python3
"""
Create a test user for the FastAPI application
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def create_test_user():
    """Create a test user"""
    print("👤 Creating test user...")
    
    user_data = {
        "phone": "+1234567890",
        "name": "Test Admin",
        "email": "admin@test.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/user_routes/create",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ User created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")

def send_otp():
    """Send OTP to the test user"""
    print("\n📧 Sending OTP...")
    
    otp_data = {
        "type": "email",
        "value": "admin@test.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/user_routes/send-otp",
            json=otp_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ OTP sent successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ OTP sending failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending OTP: {str(e)}")

def login_with_otp():
    """Login with OTP"""
    print("\n🔐 Logging in with OTP...")
    
    login_data = {
        "identifier": "admin@test.com",
        "role": 5,  # Admin role
        "otp": "123456"  # Default OTP for testing
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/token/admin-login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Login successful!")
            token_data = response.json()
            print(f"Access Token: {token_data.get('access_token', '')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def main():
    print("🚀 Creating Test User & Getting Token")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Create user
    create_test_user()
    
    # Step 2: Send OTP
    send_otp()
    
    # Step 3: Login
    token = login_with_otp()
    
    if token:
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! You can now test the rewards system with this token:")
        print(f"Token: {token}")
        print("\nUse this token in Authorization header:")
        print(f"Authorization: Bearer {token}")
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED! Check the error messages above.")

if __name__ == "__main__":
    main()
