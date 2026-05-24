#!/usr/bin/env python3
"""
Simple Rewards Tables Addition
Add rewards tables to existing database without complex imports
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models.rewards import (
    UserReferral, UserWallet, WalletTransaction, Coupon, CouponRedemption,
    DailyEngagement, RewardSettings, FraudDetection, Leaderboard
)

def add_rewards_tables():
    """Add rewards system tables to existing database"""
    print("🔧 Adding Rewards Tables to Existing Database...")
    
    try:
        # Create only the rewards tables
        Base.metadata.create_all(bind=engine, tables=[
            UserReferral.__table__,
            UserWallet.__table__,
            WalletTransaction.__table__,
            Coupon.__table__,
            CouponRedemption.__table__,
            DailyEngagement.__table__,
            RewardSettings.__table__,
            FraudDetection.__table__,
            Leaderboard.__table__
        ])
        
        print("✅ Rewards tables added to existing database!")
        
        # Initialize default settings manually
        from sqlalchemy.orm import sessionmaker
        from models.rewards import RewardSettings
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if settings already exist
            existing_settings = db.query(RewardSettings).count()
            
            if existing_settings == 0:
                # Add default settings
                default_settings = [
                    RewardSettings(setting_key="referral_bonus_coins", setting_value=50, description="Coins given to referrer for successful referral"),
                    RewardSettings(setting_key="welcome_bonus_coins", setting_value=20, description="Coins given to new user for successful referral"),
                    RewardSettings(setting_key="daily_login_coins", setting_value=5, description="Coins for daily login"),
                    RewardSettings(setting_key="article_read_coins", setting_value=10, description="Coins for reading an article"),
                    RewardSettings(setting_key="article_read_limit", setting_value=5, description="Max articles per day for rewards"),
                    RewardSettings(setting_key="news_share_coins", setting_value=8, description="Coins for sharing news"),
                    RewardSettings(setting_key="news_share_limit", setting_value=3, description="Max shares per day for rewards"),
                    RewardSettings(setting_key="comment_coins", setting_value=5, description="Coins for posting a comment"),
                    RewardSettings(setting_key="comment_limit", setting_value=10, description="Max comments per day for rewards"),
                    RewardSettings(setting_key="streak_bonus_coins", setting_value=50, description="Bonus coins for weekly streak"),
                ]
                
                for setting in default_settings:
                    db.add(setting)
                
                db.commit()
                print("✅ Default reward settings initialized!")
            else:
                print("ℹ️ Reward settings already exist")
            
        finally:
            db.close()
        
        print("\n🎯 **Tables Added to news_platform.db:**")
        print("   • user_referrals - Referral tracking")
        print("   • user_wallets - User coin wallets")
        print("   • wallet_transactions - Transaction history")
        print("   • coupons - Coupon system")
        print("   • coupon_redemptions - Redemption tracking")
        print("   • daily_engagement - Daily engagement tracking")
        print("   • reward_settings - System configuration")
        print("   • fraud_detection - Fraud prevention")
        print("   • leaderboard - User rankings")
        
        print("\n🚀 **Rewards system is ready in your existing database!**")
        
    except Exception as e:
        print(f"❌ Error adding tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = add_rewards_tables()
    if success:
        print("\n🎉 **Tables added successfully to news_platform.db!**")
        print("\n📝 **Next Steps:**")
        print("   1. Start server: python -m uvicorn main:app --port 8001 --host 0.0.0.0 --reload")
        print("   2. Open: http://localhost:8001/docs")
        print("   3. Look for 'Rewards' section")
        print("\n🎯 **Test Endpoints:**")
        print("   • GET /rewards/referral - Get referral info")
        print("   • GET /rewards/wallet - Get wallet balance")
        print("   • POST /rewards/daily-login - Claim daily reward")
        print("   • POST /rewards/article-read - Claim reading reward")
        print("   • GET /rewards/coupons - Available coupons")
        print("   • GET /rewards/leaderboard - User rankings")
    else:
        print("\n❌ **Failed to add tables!**")
        sys.exit(1)
