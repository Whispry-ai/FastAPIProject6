#!/usr/bin/env python3
"""
Deep Database Debug
Check exact database content and structure
"""

import sqlite3

def debug_database_content():
    """Debug database content thoroughly"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        print("🔍 Deep Database Debug")
        print("=" * 50)
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("📋 Users table structure:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - NULL: {col[3]}, Default: {col[4]}")
        
        print("\n👥 All users in database:")
        cursor.execute("SELECT user_uid, phone, email, role FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"   UID: {user[0]}, Phone: '{user[1]}', Email: '{user[2]}', Role: {user[3]}")
        
        print("\n🔍 Search for phone '8967452312':")
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone = ?", ("8967452312",))
        exact_match = cursor.fetchone()
        
        if exact_match:
            print(f"   ✅ Exact match found: {exact_match}")
        else:
            print("   ❌ No exact match found")
        
        print("\n🔍 Search for phone LIKE '%8967452312%':")
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone LIKE ?", ("%8967452312%",))
        like_match = cursor.fetchall()
        
        if like_match:
            for match in like_match:
                print(f"   📱 Partial match: {match}")
        else:
            print("   ❌ No partial matches found")
        
        print("\n🔍 Check for any NULL phones:")
        cursor.execute("SELECT user_uid, phone, email FROM users WHERE phone IS NULL")
        null_phones = cursor.fetchall()
        
        if null_phones:
            for user in null_phones:
                print(f"   ⚠️  NULL phone: {user}")
        else:
            print("   ✅ No NULL phones found")
        
        # Test the exact query that login uses
        print("\n🧪 Testing login query:")
        cursor.execute("SELECT * FROM users WHERE (email = ? OR phone = ?)", ("8967452312", "8967452312"))
        login_query_result = cursor.fetchone()
        
        if login_query_result:
            print(f"   ✅ Login query found: {login_query_result[:4]}")
        else:
            print("   ❌ Login query returned nothing")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def recreate_user_correctly():
    """Recreate user with correct format"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Delete existing user if exists
        cursor.execute("DELETE FROM users WHERE phone = ?", ("8967452312",))
        
        # Create user with exact format
        cursor.execute("""
            INSERT INTO users (user_uid, phone, email, role, created_at, activated_at, mobile_verified, email_verified)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), 1, 0)
        """, (
            "USER8967",  # user_uid
            "8967452312",  # phone
            "test8967@example.com",  # email
            4  # role
        ))
        
        conn.commit()
        
        # Verify creation
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone = ?", ("8967452312",))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User recreated successfully:")
            print(f"   UID: {user[0]}, Phone: '{user[1]}', Email: '{user[2]}', Role: {user[3]}")
        else:
            print("❌ User creation failed")
        
        conn.close()
        return user is not None
        
    except Exception as e:
        print(f"❌ Error recreating user: {e}")
        return False

def main():
    """Main function"""
    debug_database_content()
    
    print("\n" + "=" * 50)
    print("🔧 Attempting to Fix User")
    print("=" * 50)
    
    if recreate_user_correctly():
        print("✅ User fix completed - try authentication again")

if __name__ == "__main__":
    main()
