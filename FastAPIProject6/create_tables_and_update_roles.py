#!/usr/bin/env python3
"""
Create database tables and update user roles
Changes ADMIN role from 4 to 5 and PUBLISHER role from 2 to 4
"""

import os
from sqlalchemy import text
from database import engine, SessionLocal, Base
from schemas import UserRole

def create_database_tables():
    """Create all database tables"""
    print("🏗️  Creating database tables...")
    
    try:
        # Import all models to ensure they're registered with Base
        from models import user, news, content, engagement, guest, base_location, insorts
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created successfully!")
        
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
        return False

def update_user_roles():
    """Update existing user roles to match new role numbers"""
    print("\n🔄 Updating user roles...")
    print(f"📊 Old roles: PUBLISHER=2, ADMIN=4")
    print(f"📊 New roles: PUBLISHER=4, ADMIN=5")
    
    try:
        with SessionLocal() as db:
            # Check if users table exists and has data
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            
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

def verify_setup():
    """Verify the complete setup"""
    print("\n🔍 Verifying setup...")
    
    try:
        with SessionLocal() as db:
            # Check tables exist
            result = db.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.fetchone()[0]
            print(f"✅ Database has {table_count} tables")
            
            # Check users table
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"✅ Users table has {user_count} records")
            
            # Verify no old roles exist
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE role IN (2)"))
            old_roles = result.fetchone()[0]
            
            if old_roles > 0:
                print(f"⚠️  Found {old_roles} users with old role numbers")
                return False
            else:
                print("✅ All users have correct role numbers")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Setup and Role Update Script")
    print("=" * 60)
    
    success = True
    
    # Step 1: Create tables
    if not create_database_tables():
        success = False
    
    # Step 2: Update roles
    if success and not update_user_roles():
        success = False
    
    # Step 3: Verify setup
    if success and verify_setup():
        print("\n🎉 Database setup and role update completed successfully!")
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
