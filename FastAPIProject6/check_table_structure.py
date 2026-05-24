#!/usr/bin/env python3
"""
Check users table structure
"""

import sqlite3

DB_PATH = "news_platform.db"

def check_table_structure():
    """Check users table columns"""
    print("🔍 Checking users table structure...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"Users table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking table: {str(e)}")

def main():
    check_table_structure()

if __name__ == "__main__":
    main()
