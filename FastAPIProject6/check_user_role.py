#!/usr/bin/env python3
"""
Check user's current role in database
"""

import sqlite3

DB_PATH = "news_platform.db"

def check_user_role():
    """Check user's current role"""
    print("🔍 Checking user's current role...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check user by email
        cursor.execute("SELECT user_uid, email, phone, name, role FROM users WHERE email = 'kamineniaswini@gmail.com'")
        user = cursor.fetchone()
        
        if user:
            user_uid, email, phone, name, role = user
            print(f"✅ User found:")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   Name: {name}")
            print(f"   Role: {role} (type: {type(role)})")
            
            role_names = {
                0: "GUEST",
                1: "USER", 
                2: "PUBLISHER",
                3: "EMPLOYEE",
                4: "REPORTER",
                5: "ADMIN"
            }
            print(f"   Role Name: {role_names.get(role, 'UNKNOWN')}")
            
            # Check all users
            cursor.execute("SELECT email, role FROM users")
            all_users = cursor.fetchall()
            print(f"\n📋 All users in database:")
            for u in all_users:
                print(f"   - {u[0]}: Role {u[1]} ({role_names.get(u[1], 'UNKNOWN')})")
        else:
            print("❌ User not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking user: {str(e)}")

def main():
    print("🚀 Check User Role")
    print("=" * 50)
    
    check_user_role()
    
    print("\n" + "=" * 50)
    print("💡 If role is not 5 (ADMIN), you need to:")
    print("   1. Update user role to 5")
    print("   2. Use correct role in login request")

if __name__ == "__main__":
    main()
