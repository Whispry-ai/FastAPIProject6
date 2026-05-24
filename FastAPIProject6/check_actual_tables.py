#!/usr/bin/env python3
"""
Check what tables actually exist in your database
"""

from database import engine
from sqlalchemy import text

def check_database_tables():
    """Check all tables in the database"""
    print("🗄️ **Checking Actual Database Tables**")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print(f"\n📊 **Found {len(tables)} tables:**")
            print("-" * 30)
            
            # Group tables by category
            news_tables = []
            user_tables = []
            engagement_tables = []
            location_tables = []
            content_tables = []
            other_tables = []
            
            for table in tables:
                if 'news' in table.lower():
                    news_tables.append(table)
                elif 'user' in table.lower():
                    user_tables.append(table)
                elif any(word in table.lower() for word in ['share', 'view', 'like', 'comment', 'reaction', 'bookmark', 'engagement']):
                    engagement_tables.append(table)
                elif any(word in table.lower() for word in ['state', 'district', 'city', 'location']):
                    location_tables.append(table)
                elif any(word in table.lower() for word in ['content', 'advertisement', 'category', 'tag']):
                    content_tables.append(table)
                else:
                    other_tables.append(table)
            
            # Display tables by category
            if news_tables:
                print(f"\n📰 **News Tables ({len(news_tables)}):**")
                for table in news_tables:
                    print(f"   • {table}")
            
            if user_tables:
                print(f"\n👤 **User Tables ({len(user_tables)}):**")
                for table in user_tables:
                    print(f"   • {table}")
            
            if engagement_tables:
                print(f"\n💬 **Engagement Tables ({len(engagement_tables)}):**")
                for table in engagement_tables:
                    print(f"   • {table}")
            
            if location_tables:
                print(f"\n📍 **Location Tables ({len(location_tables)}):**")
                for table in location_tables:
                    print(f"   • {table}")
            
            if content_tables:
                print(f"\n📄 **Content Tables ({len(content_tables)}):**")
                for table in content_tables:
                    print(f"   • {table}")
            
            if other_tables:
                print(f"\n🔧 **Other Tables ({len(other_tables)}):**")
                for table in other_tables:
                    print(f"   • {table}")
            
            # Check specific engagement tables
            print(f"\n🔍 **Checking Specific Engagement Tables:**")
            specific_tables = ['shares', 'news_views', 'reactions', 'likes', 'comments', 'bookmarks']
            
            for table in specific_tables:
                if table in tables:
                    print(f"   ✅ {table} - EXISTS")
                    
                    # Check if it has data
                    try:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        print(f"      📊 Records: {count}")
                    except:
                        print(f"      ❓ Could not count records")
                else:
                    print(f"   ❌ {table} - NOT FOUND")
            
            # Check news table columns for counters
            print(f"\n📋 **News Table Columns (Counters):**")
            if 'news' in tables:
                try:
                    columns_result = conn.execute(text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'news' 
                        AND column_name LIKE '%_count'
                        ORDER BY column_name
                    """))
                    
                    counter_columns = columns_result.fetchall()
                    if counter_columns:
                        for col, dtype in counter_columns:
                            print(f"   ✅ {col} ({dtype})")
                    else:
                        print(f"   ❓ No counter columns found")
                        
                except Exception as e:
                    print(f"   ❌ Error checking columns: {e}")
            else:
                print(f"   ❌ News table not found")
            
            print(f"\n🎯 **Summary:**")
            print(f"   • Total tables: {len(tables)}")
            print(f"   • News tables: {len(news_tables)}")
            print(f"   • User tables: {len(user_tables)}")
            print(f"   • Engagement tables: {len(engagement_tables)}")
            print(f"   • Location tables: {len(location_tables)}")
            print(f"   • Content tables: {len(content_tables)}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_tables()
