#!/usr/bin/env python3
"""
Execute rewards endpoints - no JSON formatting, just execute
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def execute_rewards_endpoints():
    """Execute rewards endpoints - simple output"""
    print("🎁 Execute Rewards Endpoints")
    print(f"Base URL: {BASE_URL}")
    print("=" * 40)
    
    # Get token first
    token = get_token()
    if not token:
        print("❌ No token - cannot test endpoints")
        return
    
    # Execute endpoints
    execute_endpoints(token)

def get_token():
    """Get authentication token"""
    print("🔐 Getting token...")
    
    try:
        # Send OTP
        otp_data = {"type": "email", "value": "test@example.com"}
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            
            # Login
            login_data = {"identifier": "test@example.com", "role": 5, "otp": otp_code}
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        
        print(f"❌ Token failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        return None

def execute_endpoints(token):
    """Execute all rewards endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎁 Executing Rewards Endpoints:")
    print("-" * 30)
    
    # List of endpoints to execute
    endpoints = [
        ("GET", "/rewards/wallet", "Wallet"),
        ("GET", "/rewards/referral/info", "Referral"),
        ("GET", "/rewards/leaderboard", "Leaderboard"),
        ("POST", "/rewards/daily/login", "Daily Reward"),
        ("GET", "/rewards/transactions/history", "Transactions"),
        ("GET", "/rewards/coupons/available", "Coupons"),
        ("POST", "/rewards/referral/claim", "Claim Referral"),
        ("GET", "/rewards/stats/overview", "Stats")
    ]
    
    success = 0
    total = len(endpoints)
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            # Simple output - no JSON formatting
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
            
            if response.status_code == 200:
                success += 1
            
        except Exception as e:
            print(f"❌ {name}: Error")
    
    print("-" * 30)
    print(f"Results: {success}/{total} working")
    
    if success == total:
        print("🎉 All rewards endpoints working!")
    elif success > 0:
        print("⚠️  Some rewards endpoints working")
    else:
        print("❌ No rewards endpoints working")

def main():
    execute_rewards_endpoints()
    
    print("\n" + "=" * 40)
    print("💡 Simple execution - no JSON formatting")
    print("🌐 Server: http://127.0.0.1:8000")
    print("📖 Docs: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()
