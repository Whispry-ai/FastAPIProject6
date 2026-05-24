#!/usr/bin/env python3
"""
Fix admin login by updating user role in database
"""

import sqlite3
import requests

BASE_URL = "http://127.0.0.1:8002"
DB_PATH = "news_platform.db"

def main():
    print("🚀 Fix Admin Login Issue")
    print("=" * 50)
    
    # Step 1: Update user role to ADMIN
    print("📝 Step 1: Updating user role to ADMIN (5)...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update user role to ADMIN
        cursor.execute("UPDATE users SET role = 5 WHERE email = 'test@example.com'")
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT user_uid, email, name, role FROM users WHERE email = 'test@example.com'")
        user = cursor.fetchone()
        
        if user:
            user_uid, email, name, role = user
            print(f"✅ User updated successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {name}")
            print(f"   Role: {role} (ADMIN)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating user: {str(e)}")
        return
    
    # Step 2: Test admin login
    print("\n🔐 Step 2: Testing admin login...")
    
    # Send OTP
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data)
        print(f"OTP Send: {response.status_code}")
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP: {otp_code}")
            
            # Login with admin role
            login_data = {
                "identifier": "test@example.com",
                "role": 5,  # ADMIN role
                "otp": otp_code
            }
            
            response = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data)
            print(f"Admin Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Admin login successful!")
                print(f"Token: {access_token[:30]}...")
                
                # Test rewards endpoints
                test_rewards_endpoints(access_token)
            else:
                print(f"❌ Admin login failed: {response.text}")
        else:
            print(f"❌ OTP send failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📖 API Documentation: http://127.0.0.1:8002/docs")

def test_rewards_endpoints(token):
    """Test rewards endpoints with admin token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Testing Rewards Endpoints...")
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet Balance"),
        ("GET", "/rewards/referral/info", "🔗 Referral Info"),
        ("POST", "/rewards/daily/login", "🎁 Daily Login Reward"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("GET", "/rewards/transactions/history", "📊 Transaction History")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"{description}: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {response.json()}")
            else:
                print(f"❌ {response.text}")
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")

if __name__ == "__main__":
    main()
