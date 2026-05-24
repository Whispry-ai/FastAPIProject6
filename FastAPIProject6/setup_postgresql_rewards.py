#!/usr/bin/env python3
"""
PostgreSQL Database Setup for Rewards System
Setup database, tables, and test data using PostgreSQL
"""

import psycopg2
from psycopg2 import sql
from datetime import datetime
import sys

class PostgreSQLSetup:
    def __init__(self):
        self.db_name = "news_platform"
        self.db_user = "postgres"
        self.db_password = "password"
        self.db_host = "localhost"
        self.db_port = "5432"
        
    def connect_to_postgres(self):
        """Connect to PostgreSQL server (without specifying database)"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database="postgres"  # Connect to default postgres database
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            print("   Make sure PostgreSQL is running and credentials are correct")
            return None
    
    def create_database(self):
        """Create the news_platform database"""
        try:
            conn = self.connect_to_postgres()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )
            
            if cursor.fetchone():
                print(f"✅ Database '{self.db_name}' already exists")
            else:
                # Create database
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name))
                )
                print(f"✅ Created database '{self.db_name}'")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def connect_to_database(self):
        """Connect to the news_platform database"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to database '{self.db_name}': {e}")
            return None
    
    def create_tables(self):
        """Create all necessary tables"""
        try:
            conn = self.connect_to_database()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_uid VARCHAR(8) UNIQUE NOT NULL,
                    phone VARCHAR(15) UNIQUE,
                    name VARCHAR,
                    gender VARCHAR,
                    role INTEGER DEFAULT 0,
                    language VARCHAR,
                    state_id INTEGER,
                    district_id INTEGER,
                    city_id INTEGER,
                    email VARCHAR(25) UNIQUE,
                    user_name VARCHAR(18) UNIQUE,
                    email_verified BOOLEAN DEFAULT FALSE,
                    mobile_verified BOOLEAN DEFAULT FALSE,
                    date_of_birth DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    token_version INTEGER DEFAULT 0,
                    is_suspended BOOLEAN DEFAULT FALSE,
                    suspension_reason VARCHAR(500),
                    suspended_at TIMESTAMP,
                    suspended_until TIMESTAMP,
                    suspended_by VARCHAR(8),
                    activated_at TIMESTAMP,
                    last_login TIMESTAMP,
                    switched_by VARCHAR(8),
                    switched_at TIMESTAMP
                )
            """)
            print("✅ Created users table")
            
            # Create user_wallets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_wallets (
                    id SERIAL PRIMARY KEY,
                    user_uid VARCHAR(8) NOT NULL REFERENCES users(user_uid),
                    current_balance INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created user_wallets table")
            
            # Create wallet_transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallet_transactions (
                    id SERIAL PRIMARY KEY,
                    wallet_id INTEGER NOT NULL REFERENCES user_wallets(id),
                    transaction_type VARCHAR(50) NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT,
                    reference_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created wallet_transactions table")
            
            # Create user_referrals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_uid VARCHAR(8) NOT NULL REFERENCES users(user_uid),
                    referred_uid VARCHAR(8) REFERENCES users(user_uid),
                    referral_code VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'PENDING',
                    reward_coins INTEGER DEFAULT 50,
                    welcome_coins INTEGER DEFAULT 20,
                    referrer_reward_given BOOLEAN DEFAULT FALSE,
                    referred_reward_given BOOLEAN DEFAULT FALSE,
                    verified_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created user_referrals table")
            
            # Create reward_settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reward_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value INTEGER NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created reward_settings table")
            
            # Create otp_tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS otp_tokens (
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(15) NOT NULL,
                    otp_code VARCHAR(10) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created otp_tokens table")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def insert_default_settings(self):
        """Insert default reward settings"""
        try:
            conn = self.connect_to_database()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            default_settings = [
                ('referral_bonus_coins', 50, 'Coins given to referrer for successful referral'),
                ('welcome_bonus_coins', 20, 'Coins given to new user for successful referral'),
                ('daily_login_coins', 5, 'Coins for daily login'),
                ('article_read_coins', 10, 'Coins for reading an article'),
                ('article_read_limit', 5, 'Max articles per day for rewards'),
                ('news_share_coins', 8, 'Coins for sharing news'),
                ('news_share_limit', 3, 'Max shares per day for rewards'),
                ('comment_coins', 3, 'Coins for posting comments'),
                ('comment_limit', 10, 'Max comments per day for rewards')
            ]
            
            for setting_key, setting_value, description in default_settings:
                cursor.execute("""
                    INSERT INTO reward_settings (setting_key, setting_value, description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (setting_key) DO NOTHING
                """, (setting_key, setting_value, description))
            
            conn.commit()
            print("✅ Inserted default reward settings")
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting settings: {e}")
            return False
    
    def create_test_user(self):
        """Create test user for rewards testing"""
        try:
            conn = self.connect_to_database()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT user_uid FROM users WHERE phone = %s", ("8967452312",))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"✅ User already exists: {existing_user[0]}")
                user_uid = existing_user[0]
            else:
                # Create user
                cursor.execute("""
                    INSERT INTO users (user_uid, phone, email, role, created_at, activated_at, mobile_verified, email_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING user_uid
                """, (
                    "USER8967",  # user_uid
                    "8967452312",
                    "test8967@example.com",
                    4,  # Publisher role
                    datetime.utcnow(),
                    datetime.utcnow(),
                    True,  # mobile_verified
                    False  # email_verified
                ))
                
                user_uid = cursor.fetchone()[0]
                print(f"✅ Created user: {user_uid}")
            
            # Create wallet
            cursor.execute("SELECT id FROM user_wallets WHERE user_uid = %s", (user_uid,))
            existing_wallet = cursor.fetchone()
            
            if not existing_wallet:
                cursor.execute("""
                    INSERT INTO user_wallets (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_uid,
                    100,  # Starting balance
                    100,  # Total earned
                    0,    # Total spent
                    0,    # Daily streak
                    0,    # Longest streak
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                print("✅ Created wallet with 100 coins")
            else:
                print("✅ Wallet already exists")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
    
    def setup_pgadmin_instructions(self):
        """Print pgAdmin setup instructions"""
        print("\n" + "=" * 60)
        print("🐘 pgAdmin Setup Instructions")
        print("=" * 60)
        print("1. Install pgAdmin 4 from: https://www.pgadmin.org/download/")
        print("2. Open pgAdmin and connect to PostgreSQL server:")
        print(f"   Host: {self.db_host}")
        print(f"   Port: {self.db_port}")
        print(f"   Username: {self.db_user}")
        print(f"   Password: {self.db_password}")
        print("3. You should see the 'news_platform' database")
        print("4. Expand 'news_platform' → 'Schemas' → 'public' → 'Tables'")
        print("5. You can now view and manage all rewards system tables")
        print("\n📊 Tables Created:")
        print("   - users (user accounts)")
        print("   - user_wallets (coin balances)")
        print("   - wallet_transactions (transaction history)")
        print("   - user_referrals (referral system)")
        print("   - reward_settings (system configuration)")
        print("   - otp_tokens (authentication)")
        print("\n🧪 Test User Created:")
        print("   Phone: 8967452312")
        print("   Email: test8967@example.com")
        print("   Role: 4 (Publisher)")
        print("   Wallet: 100 coins")
    
    def run_complete_setup(self):
        """Run complete PostgreSQL setup"""
        print("🚀 PostgreSQL Database Setup for Rewards System")
        print("=" * 60)
        
        steps = [
            ("Creating database", self.create_database),
            ("Creating tables", self.create_tables),
            ("Inserting default settings", self.insert_default_settings),
            ("Creating test user", self.create_test_user)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if step_func():
                print(f"✅ {step_name} completed")
            else:
                print(f"❌ {step_name} failed")
                return False
        
        self.setup_pgadmin_instructions()
        return True

def main():
    """Main function"""
    setup = PostgreSQLSetup()
    setup.run_complete_setup()

if __name__ == "__main__":
    main()
