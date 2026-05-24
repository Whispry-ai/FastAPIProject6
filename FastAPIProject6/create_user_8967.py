#!/usr/bin/env python3
"""
Create User with Phone 8967452312 for Rewards Testing
"""

import sqlite3
from datetime import datetime

def create_user_with_phone():
    """Create user with phone 8967452312"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE phone = ?", ("8967452312",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ User already exists")
            print(f"   User UID: {existing_user[1]}")
            print(f"   Phone: {existing_user[2]}")
            print(f"   Role: {existing_user[5]}")
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (user_uid, phone, email, role, created_at, activated_at, mobile_verified, email_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "USER8967",  # user_uid
                "8967452312",
                "test8967@example.com", 
                4,  # Publisher role
                datetime.utcnow(),
                datetime.utcnow(),
                True,  # mobile_verified
                False  # email_verified
            ))
            
            conn.commit()
            print("✅ User created successfully")
            print("   User UID: USER8967")
            print("   Phone: 8967452312")
            print("   Email: test8967@example.com")
            print("   Role: 4 (Publisher)")
        
        # Create wallet for the user
        user_uid = "USER8967"
        cursor.execute("SELECT * FROM user_wallets WHERE user_uid = ?", (user_uid,))
        existing_wallet = cursor.fetchone()
        
        if not existing_wallet:
            cursor.execute("""
                INSERT INTO user_wallets (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_uid,
                100,  # Starting balance
                100,  # Total earned
                0,    # Total spent
                0,    # Daily streak
                0,    # Longest streak
                datetime.utcnow(),
                datetime.utcnow()
            ))
            conn.commit()
            print("✅ Wallet created with 100 coins")
        else:
            print("✅ Wallet already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating User with Phone 8967452312")
    print("=" * 50)
    create_user_with_phone()
