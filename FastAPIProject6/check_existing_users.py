#!/usr/bin/env python3
"""
Check existing users in database and test rewards
"""

import sqlite3
import requests
import json

BASE_URL = "http://127.0.0.1:8002"
DB_PATH = "news_platform.db"

def check_existing_users():
    """Check if users exist in database"""
    print("🔍 Checking existing users in database...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Users table doesn't exist")
            return []
        
        # Get existing users
        cursor.execute("SELECT user_uid, email, phone, name, role FROM users LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            print(f"✅ Found {len(users)} users:")
            for user in users:
                print(f"   - {user[3]} ({user[1]}) - Role: {user[4]}")
        else:
            print("❌ No users found in database")
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ Error checking users: {str(e)}")
        return []

def test_login_with_user(user_email, user_phone, role=1):
    """Test login with existing user"""
    print(f"\n🔐 Testing login with {user_email}...")
    
    # Send OTP first
    otp_data = {
        "type": "email",
        "value": user_email
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/send-otp", json=otp_data)
        print(f"OTP send: {response.status_code}")
        if response.status_code != 200:
            print(f"OTP send failed: {response.text}")
    except Exception as e:
        print(f"OTP send error: {str(e)}")
    
    # Try login with default OTP
    login_data = {
        "identifier": user_email,
        "role": role,
        "otp": "123456"  # Try default OTP
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/token/verify/login", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:30]}...")
            return access_token
        else:
            print(f"Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def test_rewards_with_token(token):
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
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Wallet error: {str(e)}")
    
    # Test referral info
    try:
        response = requests.get(f"{BASE_URL}/rewards/referral/info", headers=headers)
        print(f"🔗 Referral Info: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Referral error: {str(e)}")

def main():
    print("🚀 Check Users & Test Rewards System")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Check existing users
    users = check_existing_users()
    
    if users:
        # Step 2: Try login with first user
        user = users[0]
        token = test_login_with_user(user[1], user[2], user[4])
        
        # Step 3: Test rewards
        test_rewards_with_token(token)
    else:
        print("\n" + "=" * 50)
        print("💡 No users found. You need to:")
        print("   1. Create users manually in database")
        print("   2. Check if there's a user creation endpoint")
        print("   3. Use admin panel to create users")
    
    print("\n" + "=" * 50)
    print("📖 API Documentation: http://127.0.0.1:8002/docs")

if __name__ == "__main__":
    main()
