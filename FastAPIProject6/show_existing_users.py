#!/usr/bin/env python3
"""
Show existing users in database
"""

import sqlite3
import json

DB_PATH = "news_platform.db"

def show_existing_users():
    """Show all existing users in database"""
    print("👥 Existing Users in Database")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Users table doesn't exist")
            return
        
        # Get all users
        cursor.execute("""
            SELECT user_uid, email, phone, name, role, created_at, is_active, email_verified, mobile_verified, token_version 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        if users:
            print(f"✅ Found {len(users)} users:")
            print("-" * 80)
            print(f"{'UID':<36} {'Email':<25} {'Name':<20} {'Role':<6} {'Active':<7} {'Email_Ver':<8} {'Mobile_Ver':<9}")
            print("-" * 80)
            
            for user in users:
                user_uid, email, phone, name, role, created_at, is_active, email_verified, mobile_verified, token_version = user
                role_name = {0: "GUEST", 1: "USER", 2: "PUBLISHER", 3: "EMPLOYEE", 4: "REPORTER", 5: "ADMIN"}.get(role, "UNKNOWN")
                active_status = "✅" if is_active else "❌"
                email_status = "✅" if email_verified else "❌"
                mobile_status = "✅" if mobile_verified else "❌"
                
                print(f"{user_uid:<36} {email:<25} {name:<20} {role_name:<6} {active_status:<7} {email_status:<8} {mobile_status:<9}")
            
            print("-" * 80)
            
            # Check user wallets
            print(f"\n💰 User Wallets:")
            cursor.execute("""
                SELECT u.user_uid, u.name, w.current_balance, w.total_earned, w.total_spent, w.daily_streak, w.longest_streak
                FROM users u
                LEFT JOIN user_wallets w ON u.user_uid = w.user_uid
                ORDER BY u.created_at DESC
            """)
            wallets = cursor.fetchall()
            
            if wallets:
                print("-" * 80)
                print(f"{'Name':<20} {'Balance':<10} {'Earned':<10} {'Spent':<10} {'Streak':<8} {'Longest':<8}")
                print("-" * 80)
                
                for wallet in wallets:
                    user_uid, name, balance, earned, spent, streak, longest = wallet
                    print(f"{name:<20} {balance:<10} {earned:<10} {spent:<10} {streak:<8} {longest:<8}")
            else:
                print("❌ No wallets found")
                
        else:
            print("❌ No users found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking users: {str(e)}")

def show_table_structure():
    """Show database table structure"""
    print("\n📊 Database Table Structure")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables in database: {len(tables)}")
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name, col_type, not_null, default_val, is_pk = col
                print(f"  - {col_name}: {col_type} {'(PK)' if is_pk else ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking table structure: {str(e)}")

def main():
    show_existing_users()
    show_table_structure()
    
    print("\n" + "=" * 50)
    print("💡 Use this information to:")
    print("   1. Login with existing user credentials")
    print("   2. Check role values for login")
    print("   3. Test rewards system with correct user data")

if __name__ == "__main__":
    main()
