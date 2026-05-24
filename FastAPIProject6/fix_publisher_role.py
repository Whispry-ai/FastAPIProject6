#!/usr/bin/env python3
"""
Fix the publisher user role from EMPLOYEE(3) to PUBLISHER(4)
"""

from database import SessionLocal
from sqlalchemy import text

def fix_publisher_role():
    """Update PUBLIS03 user role from EMPLOYEE to PUBLISHER"""
    print("🔧 Fixing publisher user role...")
    
    try:
        with SessionLocal() as db:
            # Update PUBLIS03 user role from 3 to 4
            result = db.execute(
                text("UPDATE users SET role = 4 WHERE user_uid = 'PUBLIS03'")
            )
            rows_updated = result.rowcount
            db.commit()
            
            if rows_updated > 0:
                print(f"✅ Updated user PUBLIS03 from EMPLOYEE(3) to PUBLISHER(4)")
            else:
                print("❌ User PUBLIS03 not found or already has correct role")
                
    except Exception as e:
        print(f"❌ Error updating user role: {e}")

if __name__ == "__main__":
    fix_publisher_role()
