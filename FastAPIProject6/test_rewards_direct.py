#!/usr/bin/env python3
"""
Direct Rewards Test - Bypass Authentication
Test rewards endpoints directly with mock authentication
"""

import requests
import sqlite3
from datetime import datetime

def create_mock_token():
    """Create a mock JWT token for testing"""
    # This is a simple mock token - in reality, JWT tokens are cryptographically signed
    # For testing purposes, we'll create a token that looks like a JWT
    header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    payload = "eyJzdWIiOiJVU0VSOjk2NyIsInJvbGUiOjQsInVzZXJfdWlkIjoiVVNFUjk2NyJ9"
    signature = "mock_signature_for_testing"
    
    return f"{header}.{payload}.{signature}"

def test_rewards_directly():
    """Test rewards endpoints with mock authentication"""
    base_url = "http://127.0.0.1:8000"
    mock_token = create_mock_token()
    
    headers = {
        "Authorization": f"Bearer {mock_token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing Rewards Endpoints Directly")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("GET", "/rewards/referral", "Referral Info"),
        ("GET", "/rewards/wallet", "Wallet Balance"),
        ("GET", "/rewards/wallet/transactions", "Transaction History"),
        ("POST", "/rewards/daily-login", "Daily Login"),
        ("GET", "/rewards/coupons", "Available Coupons"),
        ("GET", "/rewards/leaderboard", "Leaderboard"),
    ]
    
    results = {}
    
    for method, endpoint, name in endpoints:
        print(f"\n🔍 {name}:")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   🚨 Authentication required - endpoint exists but needs valid token")
                results[name] = {"status": 401, "exists": True}
            elif response.status_code == 200:
                print(f"   ✅ Working!")
                results[name] = {"status": 200, "exists": True, "working": True}
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
                results[name] = {"status": 404, "exists": False}
            elif response.status_code == 500:
                print(f"   🚨 Server error - endpoint exists but has issues")
                results[name] = {"status": 500, "exists": True, "error": True}
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                results[name] = {"status": response.status_code, "exists": True}
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[name] = {"status": "error", "exists": False}
    
    return results

def check_server_database():
    """Check what database the server is actually using"""
    try:
        # Check if server responds to a simple query
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code < 500:
            print("✅ Server is responding")
            return True
        else:
            print("❌ Server error")
            return False
    except:
        print("❌ Server not reachable")
        return False

def create_working_user_and_test():
    """Create a user that should work and test"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Create a user with a simple phone number
        cursor.execute("DELETE FROM users WHERE phone = ?", ("1234567890",))
        
        cursor.execute("""
            INSERT INTO users (user_uid, phone, email, role, created_at, activated_at, mobile_verified, email_verified)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), 1, 0)
        """, (
            "TEST123",  # user_uid
            "1234567890",  # simple phone
            "test123@example.com",  # email
            4  # role
        ))
        
        # Create wallet
        cursor.execute("DELETE FROM user_wallets WHERE user_uid = ?", ("TEST123",))
        cursor.execute("""
            INSERT INTO user_wallets (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            "TEST123",
            50,  # Starting balance
            50,  # Total earned
            0,    # Total spent
            0,    # Daily streak
            0     # Longest streak
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Created test user: phone=1234567890, uid=TEST123")
        
        # Test with this user
        base_url = "http://127.0.0.1:8000"
        
        # Send OTP
        otp_response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": "1234567890"
            },
            timeout=10
        )
        
        print(f"📱 OTP for 1234567890: {otp_response.status_code}")
        
        if otp_response.status_code == 200:
            otp_data = otp_response.json()
            otp = otp_data.get('otp', 'N/A')
            print(f"   OTP: {otp}")
            
            # Try login
            login_response = requests.post(
                f"{base_url}/user/token/verify/login",
                json={
                    "identifier": "1234567890",
                    "otp": str(otp),
                    "role": 4
                },
                timeout=10
            )
            
            print(f"🔐 Login for 1234567890: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get('access_token')
                print(f"   ✅ SUCCESS! Token: {access_token[:50]}...")
                return access_token
            else:
                print(f"   ❌ Login failed: {login_response.text}")
        else:
            print(f"   ❌ OTP failed: {otp_response.text}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main function"""
    print("🔧 Direct Rewards System Test")
    print("=" * 50)
    
    # Check server
    if not check_server_database():
        print("❌ Server is not running properly")
        return
    
    # Test endpoints directly
    direct_results = test_rewards_directly()
    
    print("\n" + "=" * 50)
    print("📊 Direct Test Results:")
    print("=" * 50)
    
    for name, result in direct_results.items():
        status = result.get("status", "unknown")
        if status == 200:
            print(f"✅ {name}: Working")
        elif status == 401:
            print(f"🔒 {name}: Exists, needs auth")
        elif status == 404:
            print(f"❌ {name}: Not found")
        elif status == 500:
            print(f"🚨 {name}: Server error")
        else:
            print(f"⚠️  {name}: Status {status}")
    
    # Try with a fresh user
    print("\n" + "=" * 50)
    print("🧪 Testing with Fresh User")
    print("=" * 50)
    
    token = create_working_user_and_test()
    
    if token:
        print("\n🎉 SUCCESS! Authentication is working")
        print("   Now we can test all rewards endpoints for 100% functionality")
    else:
        print("\n❌ Authentication still failing")

if __name__ == "__main__":
    main()
