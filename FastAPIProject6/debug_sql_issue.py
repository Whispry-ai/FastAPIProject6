#!/usr/bin/env python3
"""
Debug SQL issue with column count
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "news_platform.db"

def debug_sql():
    """Debug SQL insertion issue"""
    print("🔍 Debugging SQL insertion...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"Users table columns:")
        for i, col in enumerate(columns):
            print(f"  {i}: {col[1]} ({col[2]})")
        
        # Try simple INSERT first
        user_uid = str(uuid.uuid4())
        
        # Build INSERT statement manually
        insert_sql = """
            INSERT OR REPLACE INTO users 
            (user_uid, email, phone, name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        print(f"\nSQL statement: {insert_sql}")
        print(f"Values: {user_uid}, publisher@example.com, +7601002909, Publisher User, 4, {datetime.now()}")
        
        # Execute with explicit parameter count
        cursor.execute(insert_sql, (user_uid, "publisher@example.com", "+7601002909", "Publisher User", 4, datetime.now()))
        
        conn.commit()
        
        # Verify user
        cursor.execute("SELECT user_uid, email, phone, name, role FROM users WHERE email = 'publisher@example.com'")
        user = cursor.fetchone()
        
        if user:
            user_uid, email, phone, name, role = user
            print(f"\n✅ Publisher user created successfully!")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   Name: {name}")
            print(f"   Role: {role} (PUBLISHER)")
            print(f"   UID: {user_uid}")
        else:
            print("\n❌ Publisher user creation failed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating publisher user: {str(e)}")
        return False

def main():
    print("🚀 Debug SQL Issue")
    print("=" * 50)
    
    debug_sql()
    
    print("\n" + "=" * 50)
    print("💡 This will help identify the exact SQL issue")

if __name__ == "__main__":
    main()
