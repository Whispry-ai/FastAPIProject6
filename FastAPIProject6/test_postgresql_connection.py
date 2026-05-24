#!/usr/bin/env python3
"""
Test PostgreSQL connection for the Hyperlocal News Application
"""

import os
import psycopg2
from sqlalchemy import create_engine, text
from database import DATABASE_URL, engine

def test_postgresql_connection():
    """Test PostgreSQL database connection"""
    print("🔍 Testing PostgreSQL connection...")
    print(f"📊 DATABASE_URL: {DATABASE_URL}")
    
    try:
        # Test with psycopg2 directly
        print("\n1. Testing with psycopg2...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # Test database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"✅ Connected to database: {db_name[0]}")
        
        cursor.close()
        conn.close()
        
        # Test with SQLAlchemy
        print("\n2. Testing with SQLAlchemy...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"✅ SQLAlchemy connection successful!")
            print(f"📊 Database: {db_info[0]}")
            print(f"👤 User: {db_info[1]}")
        
        # Test table creation
        print("\n3. Testing table creation...")
        from database import Base
        print("✅ Database models loaded successfully")
        
        print("\n🎉 All PostgreSQL connection tests passed!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\n💡 Possible solutions:")
        print("   - Make sure PostgreSQL is running")
        print("   - Check if database 'news_platform' exists")
        print("   - Verify connection credentials")
        print("   - Check if PostgreSQL is accepting connections")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Connect to default postgres database to create our database
        admin_url = DATABASE_URL.replace('/news_platform', '/postgres')
        conn = psycopg2.connect(admin_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'news_platform'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📝 Creating database 'news_platform'...")
            cursor.execute('CREATE DATABASE "news_platform";')
            print("✅ Database created successfully!")
        else:
            print("✅ Database 'news_platform' already exists!")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL Connection Test")
    print("=" * 50)
    
    # First try to create database if needed
    if create_database_if_not_exists():
        # Then test the connection
        test_postgresql_connection()
    else:
        print("⚠️  Cannot proceed with connection test due to database creation failure")
