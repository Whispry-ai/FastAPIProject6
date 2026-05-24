#!/usr/bin/env python3
"""
Final Rewards Tables Creation
Simple version without import conflicts
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

def create_rewards_tables():
    """Create rewards system tables"""
    print("🔧 Creating Rewards Tables...")
    
    try:
        # Create all rewards tables
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
        
        print("✅ Rewards tables created successfully!")
        
        # Add default settings
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if settings exist
            settings_count = db.query(RewardSettings).count()
            
            if settings_count == 0:
                # Add default settings
                settings_data = [
                    ("referral_bonus_coins", 50, "Coins given to referrer for successful referral"),
                    ("welcome_bonus_coins", 20, "Coins given to new user for successful referral"),
                    ("daily_login_coins", 5, "Coins for daily login"),
                    ("article_read_coins", 10, "Coins for reading an article"),
                    ("article_read_limit", 5, "Max articles per day for rewards"),
                    ("news_share_coins", 8, "Coins for sharing news"),
                    ("news_share_limit", 3, "Max shares per day for rewards"),
                    ("comment_coins", 5, "Coins for posting a comment"),
                    ("comment_limit", 10, "Max comments per day for rewards"),
                    ("streak_bonus_coins", 50, "Bonus coins for weekly streak"),
                ]
                
                for key, value, description in settings_data:
                    setting = RewardSettings(
                        setting_key=key,
                        setting_value=value,
                        description=description
                    )
                    db.add(setting)
                
                db.commit()
                print("✅ Default reward settings added!")
            else:
                print("ℹ️ Reward settings already exist")
            
        finally:
            db.close()
        
        print("\n🎯 **Tables Created:**")
        print("   • user_referrals - Referral tracking")
        print("   • user_wallets - User coin wallets")
        print("   • wallet_transactions - Transaction history")
        print("   • coupons - Coupon system")
        print("   • coupon_redemptions - Redemption tracking")
        print("   • daily_engagement - Daily engagement tracking")
        print("   • reward_settings - System configuration")
        print("   • fraud_detection - Fraud prevention")
        print("   • leaderboard - User rankings")
        
        print("\n🚀 **Rewards system is ready!**")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_rewards_tables()
    if success:
        print("\n🎉 **Rewards system setup complete!**")
        print("\n📝 **Next Steps:**")
        print("   1. Start server: python -m uvicorn main:app --port 8001 --host 0.0.0.0 --reload")
        print("   2. Open: http://localhost:8001/docs")
        print("   3. Look for 'Rewards' section")
        print("\n🎯 **Key Features:**")
        print("   • Referral System - 50 coins per referral")
        print("   • Daily Login - 5 coins + streak bonuses")
        print("   • Article Reading - 10 coins (max 5/day)")
        print("   • News Sharing - 8 coins (max 3/day)")
        print("   • Comments - 5 coins (max 10/day)")
        print("   • Coupon System - Redeem coins for rewards")
        print("   • Leaderboard - User rankings")
        print("   • Fraud Prevention - Duplicate detection")
    else:
        print("\n❌ **Setup failed!**")
        sys.exit(1)
