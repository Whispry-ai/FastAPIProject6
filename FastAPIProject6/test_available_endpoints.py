#!/usr/bin/env python3
"""
Test all available endpoints to find correct paths
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_endpoints():
    """Test various endpoint paths"""
    print("🔍 Testing Available Endpoints...")
    
    # Test different path variations for user endpoints
    user_endpoints = [
        "/user_routes/send-otp",
        "/user/send-otp", 
        "/users/send-otp",
        "/send-otp",
        "/auth/send-otp",
        "/user/auth/send-otp",
        "/api/user/send-otp"
    ]
    
    login_endpoints = [
        "/user_routes/token/verify/login",
        "/user/token/verify/login",
        "/users/token/verify/login", 
        "/token/verify/login",
        "/auth/login",
        "/user/auth/login",
        "/api/user/login"
    ]
    
    rewards_endpoints = [
        "/rewards/wallet/balance",
        "/rewards/wallet",
        "/rewards/balance",
        "/wallet/balance",
        "/rewards/",
        "/rewards"
    ]
    
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    login_data = {
        "identifier": "test@example.com",
        "role": 1,
        "otp": "123456"
    }
    
    print("\n📱 Testing OTP endpoints:")
    for endpoint in user_endpoints:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=otp_data)
            print(f"POST {endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"POST {endpoint}: ERROR - {str(e)}")
    
    print("\n🔐 Testing Login endpoints:")
    for endpoint in login_endpoints:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=login_data)
            print(f"POST {endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"POST {endpoint}: ERROR - {str(e)}")
    
    print("\n🎁 Testing Rewards endpoints:")
    for endpoint in rewards_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"GET {endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {str(e)}")

def test_main_endpoints():
    """Test main application endpoints"""
    print("\n🏠 Testing Main Application:")
    
    main_endpoints = [
        "/",
        "/docs",
        "/openapi.json",
        "/health",
        "/status"
    ]
    
    for endpoint in main_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {str(e)}")

def main():
    print("🚀 Endpoint Discovery Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    test_main_endpoints()
    test_endpoints()
    
    print("\n" + "=" * 60)
    print("💡 Check the working endpoints above to find correct paths")
    print("📖 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
