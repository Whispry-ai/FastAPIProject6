"""
Rewards System API Routes
Complete API endpoints for referral, wallet, and coupon systems
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from services.rewards_service import RewardsService
# Direct imports to avoid package conflicts
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.rewards import (
    ReferralResponse, VerifyReferral, ReferralVerificationResponse,
    WalletBalance, TransactionHistory, DailyLoginReward, ArticleReadReward,
    NewsShareReward, CommentReward, CouponCreate, CouponResponse, CouponRedeem,
    CouponRedemptionResponse, RewardSettingsCreate, RewardSettingsResponse,
    AdminWalletAdjustment, LeaderboardEntry, LeaderboardResponse, RewardsAnalytics, EngagementAnalytics
)
from auth.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/rewards", tags=["Rewards"])

# Dependency to get rewards service
def get_rewards_service(db: Session = Depends(get_db)) -> RewardsService:
    service = RewardsService(db)
    service.initialize_default_settings()
    return service

# Referral System
@router.get("/referral", response_model=ReferralResponse)
async def get_referral_info(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get user's referral information"""
    try:
        # Generate referral code if user doesn't have one
        referral_code = rewards_service.generate_referral_code(current_user.user_uid)
        
        # Get referral statistics
        from models.rewards import UserReferral, ReferralStatus
        
        total_referrals = rewards_service.db.query(UserReferral).filter(
            UserReferral.referrer_uid == current_user.user_uid
        ).count()
        
        pending_referrals = rewards_service.db.query(UserReferral).filter(
            UserReferral.referrer_uid == current_user.user_uid,
            UserReferral.status == ReferralStatus.PENDING
        ).count()
        
        completed_referrals = rewards_service.db.query(UserReferral).filter(
            UserReferral.referrer_uid == current_user.user_uid,
            UserReferral.status == ReferralStatus.COMPLETED
        ).count()
        
        # Calculate total coins earned from referrals
        from models.rewards import TransactionType
        wallet = rewards_service.get_or_create_wallet(current_user.user_uid)
        referral_coins = rewards_service.db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.id,
            WalletTransaction.transaction_type == TransactionType.REFERRAL_BONUS
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        return ReferralResponse(
            referral_code=referral_code,
            referral_link=f"https://yourapp.com/signup?ref={referral_code}",
            total_referrals=total_referrals,
            pending_referrals=pending_referrals,
            completed_referrals=completed_referrals,
            total_coins_earned=int(referral_coins)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get referral info: {str(e)}")

@router.post("/referral/verify", response_model=ReferralVerificationResponse)
async def verify_referral(
    referral_data: VerifyReferral,
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Verify referral code during signup"""
    try:
        return rewards_service.process_referral_signup(
            user_uid="",  # Will be set during actual signup
            referral_code=referral_data.referral_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify referral: {str(e)}")

@router.post("/referral/complete", response_model=ReferralVerificationResponse)
async def complete_referral(
    verification_method: str = Query(..., regex="^(otp|first_activity)$"),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Complete referral reward after verification"""
    try:
        return rewards_service.complete_referral_reward(
            user_uid=current_user.user_uid,
            verification_method=verification_method
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete referral: {str(e)}")

# Wallet System
@router.get("/wallet", response_model=WalletBalance)
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get user's wallet balance"""
    try:
        return rewards_service.get_wallet_balance(current_user.user_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balance: {str(e)}")

@router.get("/wallet/transactions", response_model=TransactionHistory)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get transaction history"""
    try:
        return rewards_service.get_transaction_history(current_user.user_uid, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")

# Engagement Rewards
@router.post("/daily-login", response_model=DailyLoginReward)
async def claim_daily_login(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Claim daily login reward"""
    try:
        return rewards_service.process_daily_login(current_user.user_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process daily login: {str(e)}")

@router.post("/article-read", response_model=ArticleReadReward)
async def claim_article_read(
    news_uid: str = Query(...),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Claim article read reward"""
    try:
        return rewards_service.process_article_read(current_user.user_uid, news_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process article read: {str(e)}")

@router.post("/news-share", response_model=NewsShareReward)
async def claim_news_share(
    news_uid: str = Query(...),
    platform: str = Query(...),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Claim news share reward"""
    try:
        return rewards_service.process_news_share(current_user.user_uid, news_uid, platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process news share: {str(e)}")

@router.post("/comment", response_model=CommentReward)
async def claim_comment_reward(
    comment_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Claim comment reward"""
    try:
        return rewards_service.process_comment_reward(current_user.user_uid, comment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process comment reward: {str(e)}")

# Coupon System
@router.get("/coupons", response_model=List[CouponResponse])
async def get_available_coupons(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get available coupons"""
    try:
        return rewards_service.get_available_coupons(current_user.user_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coupons: {str(e)}")

@router.post("/coupons/redeem", response_model=CouponRedemptionResponse)
async def redeem_coupon(
    coupon_data: CouponRedeem,
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Redeem coupon"""
    try:
        return rewards_service.redeem_coupon(current_user.user_uid, coupon_data.coupon_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to redeem coupon: {str(e)}")

# Leaderboard
@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get leaderboard"""
    try:
        return rewards_service.get_leaderboard(limit, current_user.user_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")

# Admin Routes
@router.post("/admin/coupons", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Create new coupon (Admin only)"""
    if current_user.role < 5:  # Admin role check
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return rewards_service.create_coupon(coupon_data, current_user.user_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create coupon: {str(e)}")

@router.post("/admin/wallet-adjust")
async def adjust_wallet(
    adjustment_data: AdminWalletAdjustment,
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Adjust user wallet (Admin only)"""
    if current_user.role < 5:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models.rewards import TransactionType
        wallet = rewards_service.get_or_create_wallet(adjustment_data.user_uid)
        
        rewards_service.add_transaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.ADMIN_ADJUSTMENT,
            amount=adjustment_data.amount,
            description=adjustment_data.reason
        )
        
        return {"success": True, "message": "Wallet adjusted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust wallet: {str(e)}")

@router.get("/admin/settings")
async def get_reward_settings(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get reward settings (Admin only)"""
    if current_user.role < 5:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models.rewards import RewardSettings
        settings = rewards_service.db.query(RewardSettings).filter(
            RewardSettings.is_active == True
        ).all()
        
        return {
            "settings": [
                {
                    "key": setting.setting_key,
                    "value": setting.setting_value,
                    "description": setting.description
                }
                for setting in settings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@router.post("/admin/settings")
async def update_reward_setting(
    setting_data: RewardSettingsCreate,
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Update reward setting (Admin only)"""
    if current_user.role < 5:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models.rewards import RewardSettings
        setting = rewards_service.db.query(RewardSettings).filter(
            RewardSettings.setting_key == setting_data.setting_key
        ).first()
        
        if setting:
            setting.setting_value = setting_data.setting_value
            setting.description = setting_data.description
        else:
            setting = RewardSettings(
                setting_key=setting_data.setting_key,
                setting_value=setting_data.setting_value,
                description=setting_data.description
            )
            rewards_service.db.add(setting)
        
        rewards_service.db.commit()
        return {"success": True, "message": "Setting updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update setting: {str(e)}")

@router.get("/admin/analytics", response_model=RewardsAnalytics)
async def get_rewards_analytics(
    current_user: User = Depends(get_current_user),
    rewards_service: RewardsService = Depends(get_rewards_service)
):
    """Get rewards analytics (Admin only)"""
    if current_user.role < 5:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models.rewards import TransactionType, CouponRedemption, UserReferral, ReferralStatus
        
        # Basic stats
        total_users = rewards_service.db.query(UserWallet).count()
        
        # Today's active users
        today = datetime.utcnow().date()
        active_users_today = rewards_service.db.query(DailyEngagement).filter(
            DailyEngagement.engagement_date >= today
        ).distinct(DailyEngagement.user_uid).count()
        
        # Coins stats
        total_coins_distributed = rewards_service.db.query(WalletTransaction).filter(
            WalletTransaction.amount > 0
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        total_coins_redeemed = rewards_service.db.query(WalletTransaction).filter(
            WalletTransaction.transaction_type == TransactionType.COUPON_REDEEM
        ).with_entities(func.sum(func.abs(WalletTransaction.amount))).scalar() or 0
        
        # Referrals and coupons
        total_referrals = rewards_service.db.query(UserReferral).filter(
            UserReferral.status == ReferralStatus.COMPLETED
        ).count()
        
        total_coupons_redeemed = rewards_service.db.query(CouponRedemption).count()
        
        # Top earners (simplified)
        top_earners = rewards_service.get_leaderboard(10)
        
        # Popular coupons (simplified)
        popular_coupons = rewards_service.get_available_coupons("")[:5]
        
        return RewardsAnalytics(
            total_users=total_users,
            active_users_today=active_users_today,
            total_coins_distributed=int(total_coins_distributed),
            total_coins_redeemed=int(total_coins_redeemed),
            total_referrals=total_referrals,
            total_coupons_redeemed=total_coupons_redeemed,
            top_earners=top_earners.entries[:10],
            popular_coupons=popular_coupons
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
