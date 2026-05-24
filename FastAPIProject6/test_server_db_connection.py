#!/usr/bin/env python3
"""
Test Server Database Connection
Test if the server can actually connect to PostgreSQL
"""

import psycopg2
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_server_database_connection():
    """Test database connection using server's configuration"""
    try:
        # Import the database configuration from the server
        from database import engine, DATABASE_URL
        
        print("🔍 Testing Server Database Connection")
        print("=" * 50)
        print(f"DATABASE_URL: {DATABASE_URL}")
        
        # Test direct connection
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        print(f"✅ Direct connection successful: {result}")
        
        # Test user query
        cursor.execute("SELECT user_uid, phone FROM users WHERE phone = %s", ("8967452312",))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found in database: {user}")
        else:
            print("❌ User not found in database")
        
        # Test SQLAlchemy engine
        print(f"\n🧪 Testing SQLAlchemy engine...")
        with engine.connect() as connection:
            result = connection.execute("SELECT user_uid, phone FROM users WHERE phone = %s", ("8967452312",))
            user_from_engine = result.fetchone()
            
            if user_from_engine:
                print(f"✅ User found via SQLAlchemy: {user_from_engine}")
            else:
                print("❌ User not found via SQLAlchemy")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_server_models():
    """Test if server models can access the database"""
    try:
        from models.user import User
        from database import get_db
        
        print(f"\n🏗️ Testing Server Models...")
        
        # Test database session
        db = next(get_db())
        
        try:
            # Test User model query
            user = db.query(User).filter(User.phone == "8967452312").first()
            
            if user:
                print(f"✅ User found via model: {user.user_uid}, {user.phone}")
                return True
            else:
                print("❌ User not found via model")
                
                # Check all users
                all_users = db.query(User).all()
                print(f"📊 Total users in database: {len(all_users)}")
                for u in all_users:
                    print(f"   {u.user_uid}: {u.phone}")
                
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def create_user_via_model():
    """Create user using server model"""
    try:
        from models.user import User
        from database import get_db
        
        print(f"\n👤 Creating user via server model...")
        
        db = next(get_db())
        
        try:
            # Check if user exists
            existing_user = db.query(User).filter(User.phone == "8967452312").first()
            
            if existing_user:
                print(f"✅ User already exists: {existing_user.user_uid}")
                return existing_user.user_uid
            else:
                # Create new user
                new_user = User(
                    user_uid="USER8967",
                    phone="8967452312",
                    email="test8967@example.com",
                    role=4,
                    mobile_verified=True,
                    email_verified=False
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                print(f"✅ User created via model: {new_user.user_uid}")
                return new_user.user_uid
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return None

def main():
    """Main function"""
    if test_server_database_connection():
        if test_server_models():
            print(f"\n✅ Server database connection is working!")
        else:
            print(f"\n🔧 Trying to create user via model...")
            user_uid = create_user_via_model()
            if user_uid:
                print(f"✅ User created, authentication should work now")
            else:
                print(f"❌ Still having issues with database connection")
    else:
        print(f"\n❌ Server cannot connect to database")

if __name__ == "__main__":
    main()
