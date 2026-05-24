#!/usr/bin/env python3
"""
Create missing database tables in correct order
"""

from sqlalchemy import text
from database import engine, SessionLocal, Base

def create_missing_tables():
    """Create missing tables in correct dependency order"""
    print("🔧 Creating missing tables...")
    
    # Define table creation order based on dependencies
    table_order = [
        ('states', """
            CREATE TABLE IF NOT EXISTS states (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            )
        """),
        ('districts', """
            CREATE TABLE IF NOT EXISTS districts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                state_id INTEGER REFERENCES states(id)
            )
        """),
        ('cities', """
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                district_id INTEGER REFERENCES districts(id)
            )
        """),
        ('users', """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) NOT NULL UNIQUE,
                phone VARCHAR(15) UNIQUE,
                name VARCHAR,
                gender VARCHAR,
                role INTEGER DEFAULT 1,
                language VARCHAR,
                state_id INTEGER REFERENCES states(id),
                district_id INTEGER REFERENCES districts(id),
                city_id INTEGER REFERENCES cities(id),
                email VARCHAR(25) UNIQUE,
                user_name VARCHAR(18) UNIQUE,
                email_verified BOOLEAN DEFAULT FALSE,
                mobile_verified BOOLEAN DEFAULT FALSE,
                date_of_birth DATE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                token_version INTEGER DEFAULT 0,
                is_suspended BOOLEAN DEFAULT FALSE,
                suspension_reason VARCHAR(500),
                suspended_at TIMESTAMP WITH TIME ZONE,
                suspended_until TIMESTAMP WITH TIME ZONE,
                suspended_by VARCHAR(8),
                activated_at TIMESTAMP WITH TIME ZONE,
                last_login TIMESTAMP WITH TIME ZONE,
                switched_by VARCHAR(8),
                switched_at TIMESTAMP WITH TIME ZONE
            )
        """),
        ('news', """
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                news_uid VARCHAR(6) NOT NULL UNIQUE,
                title VARCHAR NOT NULL,
                summary VARCHAR,
                image_url VARCHAR,
                language_id INTEGER REFERENCES languages(id),
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                city_id INTEGER REFERENCES cities(id),
                source_url VARCHAR,
                source_name VARCHAR,
                is_approved BOOLEAN DEFAULT FALSE,
                approved_by_uid VARCHAR(8) REFERENCES users(user_uid),
                rejected_by_uid VARCHAR(8) REFERENCES users(user_uid),
                is_published BOOLEAN DEFAULT FALSE,
                published_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """),
        ('reactions', """
            CREATE TABLE IF NOT EXISTS reactions (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                news_uid VARCHAR(6) REFERENCES news(news_uid) ON DELETE CASCADE,
                reaction_type VARCHAR NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                UNIQUE(user_uid, news_uid)
            )
        """),
        ('comments', """
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                news_uid VARCHAR(6) REFERENCES news(news_uid) ON DELETE CASCADE,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """),
        ('shares', """
            CREATE TABLE IF NOT EXISTS shares (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                news_uid VARCHAR(6) REFERENCES news(news_uid) ON DELETE CASCADE,
                shared_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                platform VARCHAR,
                UNIQUE(user_uid, news_uid)
            )
        """),
        ('news_views', """
            CREATE TABLE IF NOT EXISTS news_views (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                news_uid VARCHAR(6) REFERENCES news(news_uid) ON DELETE CASCADE,
                viewed_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """),
        ('bookmarks', """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                content_type VARCHAR NOT NULL,
                content_id INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                UNIQUE(user_uid, content_type, content_id)
            )
        """),
        ('guest_users', """
            CREATE TABLE IF NOT EXISTS guest_users (
                id SERIAL PRIMARY KEY,
                guest_uid VARCHAR(10) NOT NULL UNIQUE,
                ip_address VARCHAR(45),
                device_id VARCHAR(100),
                device_name VARCHAR(100),
                android_version VARCHAR(20),
                app_version VARCHAR(20),
                app_version_code VARCHAR(10),
                created_at TIMESTAMP WITH TIME ZONE,
                state_id INTEGER REFERENCES states(id),
                district_id INTEGER REFERENCES districts(id),
                city_id INTEGER REFERENCES cities(id)
            )
        """),
        ('guest_preferences', """
            CREATE TABLE IF NOT EXISTS guest_preferences (
                id SERIAL PRIMARY KEY,
                guest_uid VARCHAR(10) REFERENCES guest_users(guest_uid) ON DELETE CASCADE,
                state_id INTEGER REFERENCES states(id),
                district_id INTEGER REFERENCES districts(id),
                city_id INTEGER REFERENCES cities(id),
                language VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                UNIQUE(guest_uid, city_id, language)
            )
        """),
        ('user_preferences', """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                language_id INTEGER REFERENCES languages(id),
                state_id INTEGER REFERENCES states(id),
                district_id INTEGER REFERENCES districts(id),
                city_id INTEGER REFERENCES cities(id),
                created_at TIMESTAMP WITHOUT TIME ZONE,
                updated_at TIMESTAMP WITHOUT TIME ZONE
            )
        """),
        ('advertisements', """
            CREATE TABLE IF NOT EXISTS advertisements (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                redirect_url VARCHAR(500),
                placement VARCHAR(50) NOT NULL,
                start_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                end_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                state_id INTEGER REFERENCES states(id),
                district_id INTEGER REFERENCES districts(id),
                city_id INTEGER REFERENCES cities(id),
                language_id INTEGER REFERENCES languages(id),
                target_gender VARCHAR(10),
                target_age_min INTEGER,
                target_age_max INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                is_approved BOOLEAN DEFAULT FALSE,
                is_premium BOOLEAN DEFAULT FALSE,
                premium_priority INTEGER DEFAULT 0,
                approved_at TIMESTAMP WITH TIME ZONE,
                approved_by VARCHAR(50),
                rejected_at TIMESTAMP WITH TIME ZONE,
                rejected_by VARCHAR(50),
                rejection_reason TEXT,
                created_by VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """),
        ('scheduled_news', """
            CREATE TABLE IF NOT EXISTS scheduled_news (
                id SERIAL PRIMARY KEY,
                news_uid VARCHAR(6) NOT NULL,
                title VARCHAR NOT NULL,
                summary VARCHAR NOT NULL,
                image_url VARCHAR,
                language_id INTEGER REFERENCES languages(id),
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                scheduled_by VARCHAR(8) REFERENCES users(user_uid),
                city_id INTEGER REFERENCES cities(id),
                source_url VARCHAR,
                source_name VARCHAR,
                scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
                published_at TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """),
        ('notifications', """
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_uid VARCHAR(8) REFERENCES users(user_uid),
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                link_url VARCHAR,
                notification_type VARCHAR,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """)
    ]
    
    try:
        with engine.connect() as conn:
            for table_name, sql in table_order:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ Created table: {table_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"ℹ️  Table {table_name} already exists")
                    else:
                        print(f"❌ Error creating {table_name}: {e}")
        
        print("\n🎉 Missing tables creation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating missing tables: {e}")
        return False

def add_foreign_keys():
    """Add missing foreign key constraints"""
    print("\n🔗 Adding foreign key constraints...")
    
    constraints = [
        ("users", """
            ALTER TABLE users 
            ADD CONSTRAINT IF NOT EXISTS fk_suspended_by 
            FOREIGN KEY (suspended_by) REFERENCES users(user_uid)
        """),
        ("users", """
            ALTER TABLE users 
            ADD CONSTRAINT IF NOT EXISTS fk_switched_by 
            FOREIGN KEY (switched_by) REFERENCES users(user_uid)
        """)
    ]
    
    try:
        with engine.connect() as conn:
            for table_name, sql in constraints:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ Added constraint to {table_name}")
                except Exception as e:
                    print(f"⚠️  Could not add constraint to {table_name}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error adding foreign keys: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fix Missing Tables Script")
    print("=" * 50)
    
    success = True
    
    if create_missing_tables():
        add_foreign_keys()
        
        print("\n🎯 Next steps:")
        print("   1. Run: python show_tables_sql.py (to verify)")
        print("   2. Run: python -m uvicorn main:app --port 8001 --reload")
    else:
        print("\n❌ Failed to create missing tables")
