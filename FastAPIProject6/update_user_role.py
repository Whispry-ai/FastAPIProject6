#!/usr/bin/env python3
"""
Update user roles in the database
Changes ADMIN role from 4 to 5 and PUBLISHER role from 2 to 4
"""

import os
from sqlalchemy import text
from database import engine, SessionLocal
from schemas import UserRole

def update_user_roles():
    """Update existing user roles to match new role numbers"""
    print("🔄 Updating user roles...")
    print(f"📊 Old roles: PUBLISHER=2, ADMIN=4")
    print(f"📊 New roles: PUBLISHER=4, ADMIN=5")
    
    try:
        with SessionLocal() as db:
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

def verify_role_update():
    """Verify the role update was successful"""
    print("\n🔍 Verifying role update...")
    
    try:
        with SessionLocal() as db:
            # Check for any users with old role numbers
            result = db.execute(
                text("SELECT COUNT(*) FROM users WHERE role IN (2)")
            )
            old_publishers = result.fetchone()[0]
            
            if old_publishers > 0:
                print(f"⚠️  Found {old_publishers} users still with old PUBLISHER role (2)")
                return False
            
            print("✅ All users have been updated to new role numbers!")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying roles: {e}")
        return False

if __name__ == "__main__":
    print("🚀 User Role Update Script")
    print("=" * 50)
    
    if update_user_roles():
        if verify_role_update():
            print("\n🎉 Role update completed successfully!")
            print("\n📝 New Role Mapping:")
            print("   GUEST = 0")
            print("   USER = 1") 
            print("   EMPLOYEE = 3")
            print("   PUBLISHER = 4")
            print("   ADMIN = 5")
        else:
            print("\n⚠️  Role update completed but verification failed")
    else:
        print("\n❌ Role update failed!")
