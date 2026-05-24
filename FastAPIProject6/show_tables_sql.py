#!/usr/bin/env python3
"""
Show all tables in PostgreSQL database
"""

from sqlalchemy import text
from database import engine

def show_tables():
    """Show all tables in the database"""
    print("📊 Database Tables")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for i, table in enumerate(tables, 1):
                    print(f"   {i:2d}. {table}")
            else:
                print("❌ No tables found")
            
            # Show table details
            print("\n📋 Table Details:")
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"   {table}: {count} records")
                except Exception as e:
                    print(f"   {table}: Error getting count - {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

def show_missing_tables():
    """Show what tables should exist but don't"""
    expected_tables = [
        'states', 'districts', 'cities', 'languages', 'categories',
        'users', 'news', 'reactions', 'comments', 'shares', 'news_views',
        'bookmarks', 'guest_users', 'guest_preferences', 'user_preferences',
        'advertisements', 'polls', 'youtube_shorts', 'insights', 'insight_pages',
        'insight_shares', 'scheduled_news', 'notifications'
    ]
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            existing_tables = {row[0] for row in result}
            
            missing = [t for t in expected_tables if t not in existing_tables]
            
            if missing:
                print(f"\n⚠️  Missing tables ({len(missing)}):")
                for table in missing:
                    print(f"   - {table}")
            else:
                print("\n✅ All expected tables exist!")
                
    except Exception as e:
        print(f"❌ Error checking missing tables: {e}")

if __name__ == "__main__":
    show_tables()
    show_missing_tables()
