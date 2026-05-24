"""
Referral & Rewards System Models
Complete database schema for referral, wallet, and coupon systems
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime

class TransactionType(enum.Enum):
    """Transaction types for wallet"""
    REFERRAL_BONUS = "referral_bonus"
    WELCOME_BONUS = "welcome_bonus"
    DAILY_LOGIN = "daily_login"
    ARTICLE_READ = "article_read"
    NEWS_SHARE = "news_share"
    COMMENT_POST = "comment_post"
    COUPON_REDEEM = "coupon_redeem"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    STREAK_BONUS = "streak_bonus"

class ReferralStatus(enum.Enum):
    """Referral status tracking"""
    PENDING = "pending"  # Referred but not verified
    VERIFIED = "verified"  # OTP verified or first activity completed
    COMPLETED = "completed"  # Rewards distributed
    CANCELLED = "cancelled"  # Fraud detected or cancelled

class CouponStatus(enum.Enum):
    """Coupon status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class UserReferral(Base):
    """User referral system"""
    __tablename__ = "user_referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, index=True)
    referred_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, index=True)
    referral_code = Column(String(10), nullable=False, unique=True, index=True)
    status = Column(Enum(ReferralStatus), default=ReferralStatus.PENDING)
    reward_coins = Column(Integer, default=50)  # Coins given to referrer
    welcome_coins = Column(Integer, default=20)  # Coins given to referred user
    referrer_reward_given = Column(Boolean, default=False)
    referred_reward_given = Column(Boolean, default=False)
    verification_method = Column(String(20))  # 'otp', 'first_activity'
    verified_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_uid])
    referred_user = relationship("User", foreign_keys=[referred_uid])
    
    
class UserWallet(Base):
    """User wallet for coins management"""
    __tablename__ = "user_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, unique=True, index=True)
    current_balance = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True))
    daily_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    transactions = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")
    
    
class WalletTransaction(Base):
    """Wallet transaction history"""
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("user_wallets.id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for credits, negative for debits
    description = Column(Text)
    reference_id = Column(String(50))  # Reference to related entity (news_uid, coupon_id, etc.)
    balance_after = Column(Integer, nullable=False)  # Balance after this transaction
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallet = relationship("UserWallet", back_populates="transactions")
    
    
class Coupon(Base):
    """Coupon system for redeeming coins"""
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    coin_cost = Column(Integer, nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    usage_limit = Column(Integer, default=None)  # None for unlimited
    usage_count = Column(Integer, default=0)
    status = Column(Enum(CouponStatus), default=CouponStatus.ACTIVE)
    image_url = Column(String(500))
    terms_conditions = Column(Text)
    created_by = Column(String(8), ForeignKey("users.user_uid"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    redemptions = relationship("CouponRedemption", back_populates="coupon", cascade="all, delete-orphan")
    
    
class CouponRedemption(Base):
    """Track coupon redemptions"""
    __tablename__ = "coupon_redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, index=True)
    user_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, index=True)
    coins_spent = Column(Integer, nullable=False)
    redemption_code = Column(String(20), unique=True)  # Unique code for user
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_used = Column(Boolean, default=False)
    
    # Relationships
    coupon = relationship("Coupon", back_populates="redemptions")
    user = relationship("User")
    
    
class DailyEngagement(Base):
    """Track daily engagement for rewards"""
    __tablename__ = "daily_engagement"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, index=True)
    engagement_date = Column(DateTime(timezone=True), nullable=False, index=True)
    login_reward_given = Column(Boolean, default=False)
    articles_read = Column(Integer, default=0)
    articles_read_reward_given = Column(Boolean, default=False)
    news_shared = Column(Integer, default=0)
    news_shared_reward_given = Column(Boolean, default=False)
    comments_posted = Column(Integer, default=0)
    comments_posted_reward_given = Column(Boolean, default=False)
    total_coins_earned = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    
class RewardSettings(Base):
    """System-wide reward settings"""
    __tablename__ = "reward_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(50), nullable=False, unique=True, index=True)
    setting_value = Column(Integer, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
class FraudDetection(Base):
    """Fraud prevention tracking"""
    __tablename__ = "fraud_detection"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, index=True)
    device_id = Column(String(100), index=True)
    ip_address = Column(String(45), index=True)
    detection_type = Column(String(50))  # 'duplicate_referral', 'multiple_accounts', 'suspicious_activity'
    is_blocked = Column(Boolean, default=False)
    blocked_until = Column(DateTime(timezone=True))
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    
class Leaderboard(Base):
    """User leaderboard for gamification"""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(8), ForeignKey("users.user_uid"), nullable=False, unique=True, index=True)
    total_coins = Column(Integer, default=0)
    referral_count = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    rank_position = Column(Integer)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    
