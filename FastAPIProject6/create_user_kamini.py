#!/usr/bin/env python3
"""
Create user kamineniaswini@gmail.com with admin role
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "news_platform.db"

def create_user():
    """Create user kamineniaswini@gmail.com"""
    print("👤 Creating user kamineniaswini@gmail.com...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create user with minimal columns
        user_uid = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (user_uid, email, phone, name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_uid, "kamineniaswini@gmail.com", "+7601002908", "Kamini Admin", 5, datetime.now()))
        
        # Create wallet
        cursor.execute("""
            INSERT OR REPLACE INTO user_wallets 
            (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_uid, 100, 100, 0, 1, 1, datetime.now()))
        
        conn.commit()
        
        # Verify user
        cursor.execute("SELECT user_uid, email, phone, name, role FROM users WHERE email = 'kamineniaswini@gmail.com'")
        user = cursor.fetchone()
        
        if user:
            user_uid, email, phone, name, role = user
            print(f"✅ User created successfully!")
            print(f"   Email: {email}")
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
    print("🚀 Create User Kamini")
    print("=" * 50)
    
    if create_user():
        print("\n" + "=" * 50)
        print("✅ User created! Now you can login with:")
        print("   Email: kamineniaswini@gmail.com")
        print("   Phone: +7601002908")
        print("   Role: 5 (ADMIN)")
        print("   Server: http://127.0.0.1:8003")
        print("\n📱 Send OTP first:")
        print("   POST /user/auth/send-otp")
        print("   {\"type\": \"email\", \"value\": \"kamineniaswini@gmail.com\"}")

if __name__ == "__main__":
    main()
