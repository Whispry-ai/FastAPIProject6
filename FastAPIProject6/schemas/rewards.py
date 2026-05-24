"""
Referral & Rewards System Schemas
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums for schemas
class TransactionType(str, Enum):
    REFERRAL_BONUS = "referral_bonus"
    WELCOME_BONUS = "welcome_bonus"
    DAILY_LOGIN = "daily_login"
    ARTICLE_READ = "article_read"
    NEWS_SHARE = "news_share"
    COMMENT_POST = "comment_post"
    COUPON_REDEEM = "coupon_redeem"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    STREAK_BONUS = "streak_bonus"

class ReferralStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CouponStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

# Base schemas
class ReferralCodeCreate(BaseModel):
    """Schema for creating referral code"""
    referral_code: str = Field(..., min_length=6, max_length=10, description="Unique referral code")

class ReferralResponse(BaseModel):
    """Schema for referral response"""
    referral_code: str
    referral_link: str
    total_referrals: int
    pending_referrals: int
    completed_referrals: int
    total_coins_earned: int

class VerifyReferral(BaseModel):
    """Schema for verifying referral"""
    referral_code: str = Field(..., min_length=6, max_length=10)
    verification_method: str = Field(..., pattern="^(otp|first_activity)$")

class ReferralVerificationResponse(BaseModel):
    """Schema for referral verification response"""
    success: bool
    message: str
    coins_awarded: Optional[int] = None
    referrer_bonus: Optional[int] = None

# Wallet schemas
class WalletBalance(BaseModel):
    """Schema for wallet balance"""
    current_balance: int
    total_earned: int
    total_spent: int
    daily_streak: int
    longest_streak: int

class TransactionCreate(BaseModel):
    """Schema for creating transaction"""
    transaction_type: TransactionType
    amount: int = Field(..., ge=1, description="Transaction amount")
    description: Optional[str] = None
    reference_id: Optional[str] = None

class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    transaction_type: str
    amount: int
    description: Optional[str]
    reference_id: Optional[str]
    balance_after: int
    created_at: datetime

class TransactionHistory(BaseModel):
    """Schema for transaction history"""
    transactions: List[TransactionResponse]
    total_count: int
    page: int
    limit: int

# Engagement reward schemas
class DailyLoginReward(BaseModel):
    """Schema for daily login reward"""
    success: bool
    coins_awarded: int
    daily_streak: int
    message: str

class ArticleReadReward(BaseModel):
    """Schema for article read reward"""
    success: bool
    coins_awarded: int
    articles_read_today: int
    max_daily_limit: int
    message: str

class NewsShareReward(BaseModel):
    """Schema for news share reward"""
    success: bool
    coins_awarded: int
    shares_today: int
    max_daily_limit: int
    message: str

class CommentReward(BaseModel):
    """Schema for comment reward"""
    success: bool
    coins_awarded: int
    comments_today: int
    max_daily_limit: int
    message: str

# Coupon schemas
class CouponCreate(BaseModel):
    """Schema for creating coupon"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    coin_cost: int = Field(..., ge=1, description="Coins required to redeem")
    expiry_date: datetime
    usage_limit: Optional[int] = Field(None, ge=1, description="Usage limit (None for unlimited)")
    image_url: Optional[str] = None
    terms_conditions: Optional[str] = None

class CouponUpdate(BaseModel):
    """Schema for updating coupon"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    coin_cost: Optional[int] = Field(None, ge=1)
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    terms_conditions: Optional[str] = None
    status: Optional[CouponStatus] = None

class CouponResponse(BaseModel):
    """Schema for coupon response"""
    id: int
    title: str
    description: str
    coin_cost: int
    expiry_date: datetime
    usage_limit: Optional[int]
    usage_count: int
    status: str
    image_url: Optional[str]
    terms_conditions: Optional[str]
    is_available: bool  # Whether user can redeem this coupon
    created_at: datetime

class CouponRedeem(BaseModel):
    """Schema for redeeming coupon"""
    coupon_id: int = Field(..., ge=1)

class CouponRedemptionResponse(BaseModel):
    """Schema for coupon redemption response"""
    success: bool
    message: str
    redemption_code: Optional[str] = None
    coins_spent: Optional[int] = None
    new_balance: Optional[int] = None

class UserCoupon(BaseModel):
    """Schema for user's redeemed coupons"""
    id: int
    coupon_id: int
    title: str
    description: str
    redemption_code: str
    redeemed_at: datetime
    is_used: bool
    expires_at: datetime

# Admin schemas
class RewardSettingsCreate(BaseModel):
    """Schema for creating reward settings"""
    setting_key: str = Field(..., min_length=1, max_length=50)
    setting_value: int = Field(..., ge=0)
    description: str = Field(..., min_length=1)

class RewardSettingsUpdate(BaseModel):
    """Schema for updating reward settings"""
    setting_value: int = Field(..., ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RewardSettingsResponse(BaseModel):
    """Schema for reward settings response"""
    id: int
    setting_key: str
    setting_value: int
    description: str
    is_active: bool
    created_at: datetime

class AdminWalletAdjustment(BaseModel):
    """Schema for admin wallet adjustment"""
    user_uid: str = Field(..., min_length=1, max_length=8)
    amount: int = Field(..., description="Can be positive or negative")
    reason: str = Field(..., min_length=1)

class UserEngagementStats(BaseModel):
    """Schema for user engagement statistics"""
    user_uid: str
    total_coins: int
    current_balance: int
    daily_streak: int
    longest_streak: int
    referral_count: int
    articles_read_today: int
    shares_today: int
    comments_today: int
    last_login: Optional[datetime]

class FraudDetectionAlert(BaseModel):
    """Schema for fraud detection alert"""
    user_uid: str
    detection_type: str
    details: str
    is_blocked: bool
    blocked_until: Optional[datetime]

# Leaderboard schemas
class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry"""
    user_uid: str
    username: Optional[str]
    total_coins: int
    referral_count: int
    current_streak: int
    rank_position: int

class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response"""
    entries: List[LeaderboardEntry]
    user_rank: Optional[LeaderboardEntry] = None
    total_users: int

# Analytics schemas
class RewardsAnalytics(BaseModel):
    """Schema for rewards analytics"""
    total_users: int
    active_users_today: int
    total_coins_distributed: int
    total_coins_redeemed: int
    total_referrals: int
    total_coupons_redeemed: int
    top_earners: List[LeaderboardEntry]
    popular_coupons: List[CouponResponse]

class EngagementAnalytics(BaseModel):
    """Schema for engagement analytics"""
    daily_logins: int
    articles_read: int
    news_shared: int
    comments_posted: int
    coupons_redeemed: int
    new_referrals: int
