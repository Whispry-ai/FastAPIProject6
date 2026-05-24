#!/usr/bin/env python3
"""
Show all users in database
"""

import sqlite3

DB_PATH = "news_platform.db"

def show_all_users():
    """Show all users in database"""
    print("👥 All Users in Database")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Total users: {user_count}")
        
        # Get all users
        cursor.execute("SELECT email, phone, name, role FROM users")
        users = cursor.fetchall()
        
        print("\nUsers:")
        role_names = {
            0: "GUEST",
            1: "USER", 
            2: "PUBLISHER",
            3: "EMPLOYEE",
            4: "REPORTER",
            5: "ADMIN"
        }
        
        for user in users:
            email, phone, name, role = user
            print(f"  - {name} ({email}) - Role: {role} ({role_names.get(role, 'UNKNOWN')})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing users: {str(e)}")

def main():
    show_all_users()
    
    print("\n" + "=" * 50)
    print("💡 Next steps:")
    print("   1. Check if kamineniaswini@gmail.com exists")
    print("   2. If not, create it with role 5 (ADMIN)")
    print("   3. Test login with correct credentials")

if __name__ == "__main__":
    main()
