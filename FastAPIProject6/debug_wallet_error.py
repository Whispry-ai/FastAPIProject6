#!/usr/bin/env python3
"""
Debug Wallet Balance Error
Find and fix the missing User attribute issue
"""

import requests
import json

def debug_wallet_error():
    """Debug the wallet balance 500 error"""
    base_url = "http://127.0.0.1:8000"
    
    # Get authentication token first
    print("🔐 Getting authentication token...")
    otp_response = requests.post(
        f"{base_url}/user/auth/send-otp",
        json={
            "type": "mobile",
            "value": "8967452312"
        },
        timeout=10
    )
    
    if otp_response.status_code != 200:
        print(f"❌ Failed to send OTP: {otp_response.text}")
        return
    
    otp_data = otp_response.json()
    otp = otp_data.get('otp', 'N/A')
    
    login_response = requests.post(
        f"{base_url}/user/token/verify/login",
        json={
            "identifier": "8967452312",
            "otp": str(otp),
            "role": 4
        },
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data.get('access_token')
    
    print(f"✅ Got token: {access_token[:50]}...")
    
    # Test wallet endpoint
    print("\n💰 Testing wallet endpoint...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    wallet_response = requests.get(
        f"{base_url}/rewards/wallet",
        headers=headers,
        timeout=10
    )
    
    print(f"Status: {wallet_response.status_code}")
    
    if wallet_response.status_code == 500:
        print(f"Error: {wallet_response.text}")
        
        # Try to understand the error
        error_detail = wallet_response.text
        if "'User' object has no attribute" in error_detail:
            print("🔍 Missing User attribute detected")
            
            # Check what attributes User object actually has
            print("\n🔍 Let's check User model attributes...")
            
            # Test different endpoints to see User object structure
            test_endpoints = [
                "/rewards/referral",
                "/rewards/daily-login"
            ]
            
            for endpoint in test_endpoints:
                try:
                    test_response = requests.get(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    print(f"   {endpoint}: {test_response.status_code}")
                except Exception as e:
                    print(f"   {endpoint}: Exception - {e}")
    
    elif wallet_response.status_code == 200:
        print("✅ Wallet endpoint working!")
        data = wallet_response.json()
        print(f"   Balance: {data.get('current_balance', 'N/A')}")

def check_user_model_attributes():
    """Check what attributes the User model has"""
    try:
        # This would normally be done by examining the User model
        # Let's check the rewards routes to see what attribute is being accessed
        
        print("🔍 Checking rewards routes for User attribute usage...")
        
        # Read the rewards routes file to find the issue
        with open('routes/rewards_routes.py', 'r') as f:
            content = f.read()
            
        # Look for current_user usage
        import re
        user_attrs = re.findall(r'current_user\.(\w+)', content)
        
        print("📋 User attributes found in rewards_routes.py:")
        for attr in set(user_attrs):
            print(f"   - {attr}")
        
        # Look specifically at wallet endpoint
        wallet_section = content[content.find('/wallet'):content.find('/wallet') + 1000]
        print(f"\n💰 Wallet endpoint section:")
        print(wallet_section[:500])
        
    except Exception as e:
        print(f"❌ Error checking attributes: {e}")

def main():
    """Main function"""
    print("🔍 Debugging Wallet Balance Error")
    print("=" * 50)
    
    debug_wallet_error()
    check_user_model_attributes()

if __name__ == "__main__":
    main()
