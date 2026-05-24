#!/usr/bin/env python3
"""
Setup Rewards Tables
Create necessary tables for rewards system
"""

import sqlite3
from datetime import datetime

def check_and_create_rewards_tables():
    """Check and create rewards system tables"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {len(existing_tables)}")
        
        # Create user_wallets table if not exists
        if 'user_wallets' not in existing_tables:
            cursor.execute("""
                CREATE TABLE user_wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_uid VARCHAR(8) NOT NULL,
                    current_balance INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_uid) REFERENCES users(user_uid)
                )
            """)
            print("✅ Created user_wallets table")
        else:
            print("✅ user_wallets table already exists")
        
        # Create wallet_transactions table if not exists
        if 'wallet_transactions' not in existing_tables:
            cursor.execute("""
                CREATE TABLE wallet_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet_id INTEGER NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT,
                    reference_id VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (wallet_id) REFERENCES user_wallets(id)
                )
            """)
            print("✅ Created wallet_transactions table")
        else:
            print("✅ wallet_transactions table already exists")
        
        # Create user_referrals table if not exists
        if 'user_referrals' not in existing_tables:
            cursor.execute("""
                CREATE TABLE user_referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_uid VARCHAR(8) NOT NULL,
                    referred_uid VARCHAR(8),
                    referral_code VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'PENDING',
                    reward_coins INTEGER DEFAULT 50,
                    welcome_coins INTEGER DEFAULT 20,
                    referrer_reward_given BOOLEAN DEFAULT FALSE,
                    referred_reward_given BOOLEAN DEFAULT FALSE,
                    verified_at DATETIME,
                    completed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_uid) REFERENCES users(user_uid),
                    FOREIGN KEY (referred_uid) REFERENCES users(user_uid)
                )
            """)
            print("✅ Created user_referrals table")
        else:
            print("✅ user_referrals table already exists")
        
        # Create reward_settings table if not exists
        if 'reward_settings' not in existing_tables:
            cursor.execute("""
                CREATE TABLE reward_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key VARCHAR(100) NOT NULL UNIQUE,
                    setting_value INTEGER NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created reward_settings table")
            
            # Insert default settings
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
            
            cursor.executemany("""
                INSERT INTO reward_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            """, default_settings)
            print("✅ Inserted default reward settings")
        else:
            print("✅ reward_settings table already exists")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Rewards tables setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_wallet_for_user():
    """Create wallet for the test user"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        # Get user_uid
        cursor.execute("SELECT user_uid FROM users WHERE phone = ?", ("+7601002908",))
        user_row = cursor.fetchone()
        
        if not user_row:
            print("❌ User not found")
            return False
        
        user_uid = user_row[0]
        
        # Check if wallet exists
        cursor.execute("SELECT * FROM user_wallets WHERE user_uid = ?", (user_uid,))
        existing_wallet = cursor.fetchone()
        
        if not existing_wallet:
            cursor.execute("""
                INSERT INTO user_wallets (user_uid, current_balance, total_earned, total_spent, daily_streak, longest_streak, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_uid,
                100,  # Starting balance - give some test coins
                100,  # Total earned
                0,    # Total spent
                0,    # Daily streak
                0,    # Longest streak
                datetime.utcnow(),
                datetime.utcnow()
            ))
            conn.commit()
            print(f"✅ Created wallet for user {user_uid} with 100 coins")
        else:
            print(f"✅ Wallet already exists for user {user_uid}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating wallet: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Setting Up Rewards System Tables")
    print("=" * 50)
    
    if check_and_create_rewards_tables():
        create_wallet_for_user()
        print("\n✅ Rewards system is ready for testing!")
    else:
        print("\n❌ Rewards setup failed")

if __name__ == "__main__":
    main()
