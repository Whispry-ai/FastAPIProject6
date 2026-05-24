#!/usr/bin/env python3
"""
Test PostgreSQL connection and basic setup
"""

from sqlalchemy import text
from database import engine, SessionLocal

def test_connection():
    """Test PostgreSQL connection"""
    print("=== PostgreSQL Connection Test ===")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connected: {version}")
            
            # Test database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"📊 Database: {db_name}")
            
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
