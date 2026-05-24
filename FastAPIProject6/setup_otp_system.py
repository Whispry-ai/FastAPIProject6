#!/usr/bin/env python3
"""
Setup OTP Tables for Authentication
Create necessary tables for OTP system
"""

import sqlite3
from datetime import datetime

def setup_otp_tables():
    """Setup OTP authentication tables"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Create otp_tokens table if not exists
        if 'otp_tokens' not in existing_tables:
            cursor.execute("""
                CREATE TABLE otp_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone VARCHAR(15) NOT NULL,
                    otp_code VARCHAR(10) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created otp_tokens table")
        else:
            print("✅ otp_tokens table already exists")
        
        # Create user_sessions table if not exists
        if 'user_sessions' not in existing_tables:
            cursor.execute("""
                CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_uid VARCHAR(8) NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    token_hash VARCHAR(255) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_uid) REFERENCES users(user_uid)
                )
            """)
            print("✅ Created user_sessions table")
        else:
            print("✅ user_sessions table already exists")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_user_exists():
    """Check if user exists in database"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone = ?", ("8967452312",))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found:")
            print(f"   User UID: {user[0]}")
            print(f"   Phone: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Role: {user[3]}")
            return True
        else:
            print("❌ User not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False

def main():
    """Main function"""
    print("🔐 Setting Up OTP Authentication System")
    print("=" * 50)
    
    if setup_otp_tables():
        if check_user_exists():
            print("\n✅ Authentication system is ready!")
        else:
            print("\n⚠️  OTP tables created but user not found")
    else:
        print("\n❌ OTP setup failed")

if __name__ == "__main__":
    main()
