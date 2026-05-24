#!/usr/bin/env python3
"""
Create Rewards System Tables
Database migration script for referral and rewards system
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
    """Create all rewards system tables"""
    print("🔧 Creating Rewards System Tables...")
    
    try:
        # Create all tables
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
        
        print("✅ Rewards system tables created successfully!")
        
        # Initialize default settings
        from services.rewards_service import RewardsService
        from database import get_db
        
        # Get a database session
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            rewards_service = RewardsService(db)
            rewards_service.initialize_default_settings()
            print("✅ Default reward settings initialized!")
            
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
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_rewards_tables()
    if success:
        print("\n🎉 **Migration completed successfully!**")
    else:
        print("\n❌ **Migration failed!**")
        sys.exit(1)
