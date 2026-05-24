#!/usr/bin/env python3
"""
Create test user directly in database and test rewards
"""

import sqlite3
import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002"
DB_PATH = "news_platform.db"

def create_test_user_direct():
    """Create test user directly in database"""
    print("👤 Creating test user directly in database...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_uid TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                name TEXT,
                role INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                mobile_verified BOOLEAN DEFAULT 0,
                token_version INTEGER DEFAULT 0
            )
        """)
        
        # Create test user
        user_uid = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (user_uid, phone, email, name, role, created_at, is_active, email_verified, mobile_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, "+1234567890", "test@example.com", "Test User", 1, datetime.now(), 1, 1, 1))
        
        # Create user_wallets table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_uid TEXT UNIQUE NOT NULL,
                current_balance INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_login_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_uid) REFERENCES users (user_uid)
            )
        """)
        
        # Create wallet for test user
        cursor.execute("""
            INSERT OR IGNORE INTO user_wallets 
            (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, 100, 100, 0, 1, 1, datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Test user created successfully!")
        print(f"   User UID: {user_uid}")
        print(f"   Email: test@example.com")
        print(f"   Phone: +1234567890")
        print(f"   Role: 1 (USER)")
        print(f"   Wallet Balance: 100 coins")
        return user_uid
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return None

def test_login_and_rewards():
    """Test login and rewards system"""
    print("\n🔐 Testing login...")
    
    # Send OTP first
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/send-otp", json=otp_data)
        print(f"OTP send: {response.status_code}")
    except Exception as e:
        print(f"OTP send error: {str(e)}")
    
    # Try login with default OTP
    login_data = {
        "identifier": "test@example.com",
        "role": 1,
        "otp": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user_routes/token/verify/login", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:30]}...")
            
            # Test rewards endpoints
            test_rewards_endpoints(access_token)
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")

def test_rewards_endpoints(token):
    """Test rewards endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Testing Rewards Endpoints...")
    
    endpoints_to_test = [
        ("GET", "/rewards/wallet/balance", "Wallet Balance"),
        ("GET", "/rewards/referral/info", "Referral Info"),
        ("POST", "/rewards/daily/login", "Daily Login Reward"),
        ("GET", "/rewards/leaderboard", "Leaderboard"),
        ("GET", "/rewards/transactions/history", "Transaction History"),
        ("POST", "/rewards/referral/claim", "Claim Referral Reward")
    ]
    
    for method, endpoint, description in endpoints_to_test:
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

def main():
    print("🚀 Direct User Creation & Rewards Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Create test user directly in database
    if create_test_user_direct():
        # Step 2: Test login and rewards
        test_login_and_rewards()
    
    print("\n" + "=" * 50)
    print("🎉 Test Complete!")
    print(f"📖 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
