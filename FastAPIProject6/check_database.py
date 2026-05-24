#!/usr/bin/env python3
"""
Simple database connection check
"""

import os
from database import DATABASE_URL

def check_database():
    """Check database connection"""
    print("🔍 Checking database connection...")
    print(f"📊 DATABASE_URL: {DATABASE_URL}")
    
    try:
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()
            print(f"✅ Connected to database: {db_name[0]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    check_database()
