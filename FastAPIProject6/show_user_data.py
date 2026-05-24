#!/usr/bin/env python3
"""
Script to display all users in the database
"""

from database import engine, SessionLocal
from sqlalchemy import text

def show_all_users():
    """Display all users in the database"""
    print("👥 Database Users Overview")
    print("=" * 50)
    
    try:
        with SessionLocal() as db:
            # Get total user count
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.fetchone()[0]
            print(f"📊 Total Users: {total_users}")
            print()
            
            if total_users == 0:
                print("❌ No users found in database")
                return
            
            # Show users by role
            print("🏷️ Users by Role:")
            print("-" * 30)
            role_result = db.execute(text("""
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role 
                ORDER BY role
            """))
            
            role_names = {
                0: "GUEST",
                1: "USER", 
                2: "PUBLISHER (OLD)",
                3: "EMPLOYEE",
                4: "PUBLISHER",
                5: "ADMIN"
            }
            
            for row in role_result:
                role_name = role_names.get(row[0], f"UNKNOWN({row[0]})")
                print(f"  {role_name}: {row[1]} users")
            
            print()
            
            # Show recent users
            print("📝 Recent Users (Last 10):")
            print("-" * 40)
            users_result = db.execute(text("""
                SELECT user_uid, name, user_name, email, phone, role, created_at, last_login
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 10
            """))
            
            for row in users_result:
                role_name = role_names.get(row[5], f"UNKNOWN({row[5]})")
                print(f"  UID: {row[0]}")
                print(f"  Name: {row[1] or 'N/A'}")
                print(f"  Username: {row[2] or 'N/A'}")
                print(f"  Email: {row[3] or 'N/A'}")
                print(f"  Phone: {row[4] or 'N/A'}")
                print(f"  Role: {role_name}")
                print(f"  Created: {row[6] or 'N/A'}")
                print(f"  Last Login: {row[7] or 'N/A'}")
                print("  " + "-" * 30)
                
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ User data analysis complete!")

def show_user_details(user_uid=None):
    """Show details for a specific user or all users"""
    if user_uid:
        print(f"🔍 Details for User: {user_uid}")
        print("=" * 50)
        
        try:
            with SessionLocal() as db:
                result = db.execute(text("""
                    SELECT * FROM users WHERE user_uid = :uid
                """), {"uid": user_uid})
                
                user = result.fetchone()
                if user:
                    print(f"User UID: {user[1]}")
                    print(f"Name: {user[3] or 'N/A'}")
                    print(f"Username: {user[12] or 'N/A'}")
                    print(f"Email: {user[11] or 'N/A'}")
                    print(f"Phone: {user[2] or 'N/A'}")
                    print(f"Gender: {user[4] or 'N/A'}")
                    print(f"Role: {user[5]}")
                    print(f"Language: {user[6] or 'N/A'}")
                    print(f"Email Verified: {user[13]}")
                    print(f"Mobile Verified: {user[14]}")
                    print(f"Created: {user[16]}")
                    print(f"Last Login: {user[20]}")
                    print(f"Suspended: {user[22]}")
                else:
                    print(f"❌ User with UID {user_uid} not found")
                    
        except Exception as e:
            print(f"❌ Error fetching user details: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Show specific user details
        show_user_details(sys.argv[1])
    else:
        # Show all users overview
        show_all_users()
