#!/usr/bin/env python3
"""
Database Setup Script for Hyperlocal News Application
This script helps set up PostgreSQL database locally
"""

import os
import psycopg2
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def setup_postgresql_database():
    """Complete PostgreSQL database setup"""
    print("🚀 PostgreSQL Database Setup")
    print("=" * 50)
    
    # Step 1: Check PostgreSQL connection
    if not check_postgresql_running():
        print("❌ PostgreSQL is not running or not accessible")
        print("\n💡 Please ensure:")
        print("   1. PostgreSQL is installed")
        print("   2. PostgreSQL service is running")
        print("   3. Connection credentials are correct")
        return False
    
    # Step 2: Create database
    if not create_database():
        print("❌ Failed to create database")
        return False
    
    # Step 3: Create tables
    if not create_tables():
        print("❌ Failed to create tables")
        return False
    
    # Step 4: Verify setup
    if not verify_setup():
        print("❌ Setup verification failed")
        return False
    
    print("🎉 Database setup completed successfully!")
    return True

def check_postgresql_running():
    """Check if PostgreSQL is running and accessible"""
    try:
        # Try to connect to default postgres database
        admin_url = DATABASE_URL.replace('/news_platform', '/postgres')
        conn = psycopg2.connect(admin_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL is running: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        return False

def create_database():
    """Create the news_platform database"""
    try:
        # Connect to postgres database to create our database
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

def create_tables():
    """Create all database tables"""
    try:
        print("📋 Creating database tables...")
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    try:
        print("🔍 Verifying database setup...")
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()
            print(f"✅ Connected to: {db_name[0]}")
            
            # List tables
            result = connection.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"✅ Created {len(tables)} tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
            
        return True
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    if setup_postgresql_database():
        print("\n🎯 Next steps:")
        print("   1. Run: python -m uvicorn main:app --port 8001 --reload")
        print("   2. Open: http://localhost:8001/docs")
        print("   3. Test your API endpoints")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
