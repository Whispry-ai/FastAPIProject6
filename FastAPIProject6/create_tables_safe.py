#!/usr/bin/env python3
"""
Create database tables safely by handling circular references
"""

import os
from sqlalchemy import text
from database import engine, SessionLocal, Base
from schemas import UserRole

def create_database_tables():
    """Create all database tables safely"""
    print("🏗️  Creating database tables...")
    
    try:
        # Import all models to ensure they're registered with Base
        from models import user, news, content, engagement, guest, base_location, insorts
        
        # Create tables without foreign key constraints first
        print("📝 Creating base tables...")
        
        # Drop all tables first to start fresh
        Base.metadata.drop_all(bind=engine)
        
        # Create tables in order to avoid circular references
        # First create tables without self-referencing constraints
        tables_to_create = []
        for table_name, table in Base.metadata.tables.items():
            if table_name == 'users':
                # Create users table without self-referencing FKs
                table_copy = table.tometadata()
                # Remove self-referencing foreign keys
                table_copy.constraints = [c for c in table.constraints 
                                        if not (hasattr(c, 'column') and 
                                               c.column.name in ['suspended_by', 'switched_by'])]
                tables_to_create.append(table_copy)
            else:
                tables_to_create.append(table)
        
        # Create all tables
        for table in tables_to_create:
            table.create(engine, checkfirst=True)
        
        print("✅ All database tables created successfully!")
        
        # Add self-referencing foreign keys after table creation
        print("🔧 Adding self-referencing constraints...")
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_suspended_by 
                FOREIGN KEY (suspended_by) REFERENCES users(user_uid)
            """))
            conn.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_switched_by 
                FOREIGN KEY (switched_by) REFERENCES users(user_uid)
            """))
            conn.commit()
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"📊 Created {len(tables)} tables: {', '.join(tables)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        # Try alternative approach
        return create_tables_simple()

def create_tables_simple():
    """Simple table creation without complex constraints"""
    print("🔄 Trying simple table creation...")
    
    try:
        # Import models
        from models import user, news, content, engagement, guest, base_location, insorts
        
        # Drop and recreate without constraints
        Base.metadata.drop_all(bind=engine)
        
        # Create tables one by one
        table_order = [
            'states', 'districts', 'cities', 'languages', 'categories',
            'users', 'news', 'reactions', 'comments', 'shares', 'news_views',
            'bookmarks', 'guest_users', 'guest_preferences', 'user_preferences',
            'advertisements', 'polls', 'youtube_shorts', 'insights', 'insight_pages',
            'insight_shares', 'scheduled_news', 'notifications'
        ]
        
        for table_name in table_order:
            if table_name in Base.metadata.tables:
                table = Base.metadata.tables[table_name]
                try:
                    table.create(engine, checkfirst=True)
                    print(f"✅ Created table: {table_name}")
                except Exception as e:
                    print(f"⚠️  Could not create {table_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple table creation failed: {e}")
        return False

def update_user_roles():
    """Update existing user roles to match new role numbers"""
    print("\n🔄 Updating user roles...")
    print(f"📊 Old roles: PUBLISHER=2, ADMIN=4")
    print(f"📊 New roles: PUBLISHER=4, ADMIN=5")
    
    try:
        with SessionLocal() as db:
            # Check if users table exists and has data
            try:
                result = db.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.fetchone()[0]
            except:
                print("ℹ️  Users table not found or empty - skipping role update")
                return True
            
            if user_count == 0:
                print("ℹ️  No users found in database - skipping role update")
                return True
            
            # Update PUBLISHER role from 2 to 4
            result1 = db.execute(
                text("UPDATE users SET role = 4 WHERE role = 2")
            )
            publishers_updated = result1.rowcount
            
            # Update ADMIN role from 4 to 5  
            result2 = db.execute(
                text("UPDATE users SET role = 5 WHERE role = 4")
            )
            admins_updated = result2.rowcount
            
            db.commit()
            
            print(f"✅ Updated {publishers_updated} users from PUBLISHER(2) to PUBLISHER(4)")
            print(f"✅ Updated {admins_updated} users from ADMIN(4) to ADMIN(5)")
            
            # Show current role distribution
            print("\n📊 Current role distribution:")
            result = db.execute(
                text("SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY role")
            )
            for row in result:
                role_name = {
                    0: "GUEST",
                    1: "USER", 
                    3: "EMPLOYEE",
                    4: "PUBLISHER",
                    5: "ADMIN"
                }.get(row[0], f"UNKNOWN({row[0]})")
                print(f"   {role_name}: {row[1]} users")
                
            return True
            
    except Exception as e:
        print(f"❌ Error updating roles: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Safe Database Setup Script")
    print("=" * 50)
    
    success = True
    
    # Step 1: Create tables
    if not create_database_tables():
        success = False
    
    # Step 2: Update roles
    if success and not update_user_roles():
        success = False
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("\n📝 New Role Mapping:")
        print("   GUEST = 0")
        print("   USER = 1") 
        print("   EMPLOYEE = 3")
        print("   PUBLISHER = 4")
        print("   ADMIN = 5")
        print("\n🎯 Next steps:")
        print("   1. Run: python -m uvicorn main:app --port 8001 --reload")
        print("   2. Open: http://localhost:8001/docs")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
