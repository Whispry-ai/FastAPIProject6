#!/usr/bin/env python3
"""
Create user with phone number 7601002908 and admin role
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "news_platform.db"

def create_phone_user():
    """Create user with phone number 7601002908"""
    print("👤 Creating user with phone 7601002908...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create user
        user_uid = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (user_uid, phone, name, role, created_at, is_active, email_verified, mobile_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, "7601002908", "Admin User", 5, datetime.now(), 1, 1, 1))
        
        # Create wallet
        cursor.execute("""
            INSERT OR REPLACE INTO user_wallets 
            (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, 100, 100, 0, 1, 1, datetime.now()))
        
        conn.commit()
        
        # Verify user
        cursor.execute("SELECT user_uid, phone, name, role FROM users WHERE phone = '7601002908'")
        user = cursor.fetchone()
        
        if user:
            user_uid, phone, name, role = user
            print(f"✅ User created successfully!")
            print(f"   Phone: {phone}")
            print(f"   Name: {name}")
            print(f"   Role: {role} (ADMIN)")
            print(f"   UID: {user_uid}")
        else:
            print("❌ User creation failed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return False

def main():
    print("🚀 Create Phone User for Admin Login")
    print("=" * 50)
    
    if create_phone_user():
        print("\n" + "=" * 50)
        print("✅ User created! Now you can login with:")
        print("   Phone: 7601002908")
        print("   Role: 5 (ADMIN)")
        print("   Server: http://127.0.0.1:8003")
        print("\n📱 Send OTP first:")
        print("   POST /user/auth/send-otp")
        print("   {\"type\": \"mobile\", \"value\": \"7601002908\"}")

if __name__ == "__main__":
    main()
