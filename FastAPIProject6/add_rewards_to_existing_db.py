#!/usr/bin/env python3
"""
Add Rewards Tables to Existing Database
Use your existing news_platform.db database
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

def add_rewards_to_existing_db():
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
    success = add_rewards_to_existing_db()
    if success:
        print("\n🎉 **Tables added successfully to news_platform.db!**")
        print("\n📝 **Next Steps:**")
        print("   1. Start server: python -m uvicorn main:app --port 8001 --host 0.0.0.0 --reload")
        print("   2. Open: http://localhost:8001/docs")
        print("   3. Look for 'Rewards' section")
    else:
        print("\n❌ **Failed to add tables!**")
        sys.exit(1)
