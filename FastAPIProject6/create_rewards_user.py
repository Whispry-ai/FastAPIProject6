#!/usr/bin/env python3
"""
Quick User Creation for Rewards Testing
Create a test user for rewards system testing
"""

import requests
import sqlite3
from datetime import datetime

def create_user_directly():
    """Create user directly in database"""
    try:
        # Connect to database
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE phone = ?", ("+7601002908",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ User already exists")
            print(f"   User UID: {existing_user[1]}")
            print(f"   Phone: {existing_user[2]}")
            print(f"   Role: {existing_user[5]}")
        else:
            # Create new user with proper schema
            cursor.execute("""
                INSERT INTO users (user_uid, phone, email, role, created_at, activated_at, mobile_verified, email_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "TEST001",  # user_uid
                "+7601002908",
                "test@example.com", 
                4,  # Publisher role
                datetime.utcnow(),
                datetime.utcnow(),
                True,  # mobile_verified
                False  # email_verified
            ))
            
            conn.commit()
            print("✅ User created successfully")
            print("   User UID: TEST001")
            print("   Phone: +7601002908")
            print("   Email: test@example.com")
            print("   Role: 4 (Publisher)")
        
        # Create wallet for the user
        user_id = cursor.execute("SELECT user_uid FROM users WHERE phone = ?", ("+7601002908",)).fetchone()[0]
        
        cursor.execute("SELECT * FROM user_wallets WHERE user_uid = ?", (user_id,))
        existing_wallet = cursor.fetchone()
        
        if not existing_wallet:
            cursor.execute("""
                INSERT INTO user_wallets (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                0,  # Starting balance
                0,  # Total earned
                0,  # Total spent
                0,  # Daily streak
                0,  # Longest streak
                datetime.utcnow(),
                datetime.utcnow()
            ))
            conn.commit()
            print("✅ Wallet created successfully")
        else:
            print("✅ Wallet already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_otp_and_login():
    """Test OTP and login after user creation"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔐 Testing OTP and Login:")
    
    # Send OTP
    try:
        response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": "+7601002908"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            otp = data.get('otp', 'N/A')
            print(f"📱 OTP sent: {otp}")
            
            # Try to login
            response = requests.post(
                f"{base_url}/user/token/verify/login",
                json={
                    "identifier": "+7601002908",
                    "otp": str(otp),
                    "role": 4
                },
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                print(f"✅ Login successful!")
                return access_token
            else:
                print(f"❌ Login failed: {response.text}")
                return None
        else:
            print(f"❌ OTP send failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Creating Test User for Rewards System")
    print("=" * 50)
    
    # Create user directly in database
    if create_user_directly():
        # Test OTP and login
        token = test_otp_and_login()
        
        if token:
            print("\n🎉 SUCCESS! User is ready for rewards testing")
            print(f"   Access Token: {token[:50]}...")
        else:
            print("\n⚠️  User created but login failed - check server")
    else:
        print("\n❌ User creation failed")

if __name__ == "__main__":
    main()
