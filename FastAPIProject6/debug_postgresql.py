#!/usr/bin/env python3
"""
Debug PostgreSQL Database
Check what's in the PostgreSQL database
"""

import psycopg2

def debug_postgresql_database():
    """Debug PostgreSQL database content"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="news_platform"
        )
        cursor = conn.cursor()
        
        print("🔍 PostgreSQL Database Debug")
        print("=" * 50)
        
        # Check users table
        cursor.execute("SELECT user_uid, phone, email, role FROM users")
        users = cursor.fetchall()
        
        print(f"👥 Users in database ({len(users)} total):")
        for user in users:
            print(f"   UID: {user[0]}, Phone: '{user[1]}', Email: '{user[2]}', Role: {user[3]}")
        
        # Search for specific phone
        print(f"\n🔍 Searching for phone '8967452312':")
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone = %s", ("8967452312",))
        exact_match = cursor.fetchone()
        
        if exact_match:
            print(f"   ✅ Found: {exact_match}")
        else:
            print("   ❌ Not found")
        
        # Test the exact login query
        print(f"\n🧪 Testing login query:")
        cursor.execute("SELECT * FROM users WHERE (email = %s OR phone = %s)", ("8967452312", "8967452312"))
        login_query_result = cursor.fetchone()
        
        if login_query_result:
            print(f"   ✅ Login query found: {login_query_result[:4]}")
        else:
            print("   ❌ Login query returned nothing")
        
        # Check wallets
        print(f"\n💰 User wallets:")
        cursor.execute("SELECT user_uid, current_balance, total_earned FROM user_wallets")
        wallets = cursor.fetchall()
        
        for wallet in wallets:
            print(f"   UID: {wallet[0]}, Balance: {wallet[1]}, Earned: {wallet[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_server_connection():
    """Test if server can connect to database"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code < 500:
            print("✅ Server is responding")
            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False

def main():
    """Main function"""
    if test_server_connection():
        debug_postgresql_database()
    else:
        print("❌ Server is not running properly")

if __name__ == "__main__":
    main()
