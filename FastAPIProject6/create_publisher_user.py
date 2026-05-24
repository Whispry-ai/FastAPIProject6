#!/usr/bin/env python3
"""
Create publisher user with role 4
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "news_platform.db"

def create_publisher_user():
    """Create publisher user with role 4"""
    print("👤 Creating publisher user (role 4)...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create publisher user
        user_uid = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (user_uid, email, phone, name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_uid, "publisher@example.com", "+7601002909", "Publisher User", 4, datetime.now()))
        
        # Create wallet
        cursor.execute("""
            INSERT OR REPLACE INTO user_wallets 
            (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, 100, 100, 0, 1, 1, datetime.now()))
        
        conn.commit()
        
        # Verify user
        cursor.execute("SELECT user_uid, email, phone, name, role FROM users WHERE email = 'publisher@example.com'")
        user = cursor.fetchone()
        
        if user:
            user_uid, email, phone, name, role = user
            print(f"✅ Publisher user created successfully!")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   Name: {name}")
            print(f"   Role: {role} (PUBLISHER)")
            print(f"   UID: {user_uid}")
        else:
            print("❌ Publisher user creation failed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating publisher user: {str(e)}")
        return False

def main():
    print("🚀 Create Publisher User (Role 4)")
    print("=" * 50)
    
    if create_publisher_user():
        print("\n" + "=" * 50)
        print("✅ Publisher user created! Login with:")
        print("   Email: publisher@example.com")
        print("   Phone: +7601002909")
        print("   Role: 4 (PUBLISHER)")
        print("   Server: http://127.0.0.1:8003")
        print("\n📱 Send OTP first:")
        print("   POST /user/auth/send-otp")
        print("   {\"type\": \"email\", \"value\": \"publisher@example.com\"}")

if __name__ == "__main__":
    main()
