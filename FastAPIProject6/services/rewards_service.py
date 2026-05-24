"""
Rewards System Service Layer
Business logic for referral, wallet, and coupon systems
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import secrets
import hashlib

from models.rewards import (
    UserReferral, UserWallet, WalletTransaction, Coupon, CouponRedemption,
    DailyEngagement, RewardSettings, FraudDetection, Leaderboard, TransactionType, ReferralStatus
)
from models.user import User
from schemas.rewards import (
    ReferralResponse, VerifyReferral, ReferralVerificationResponse,
    WalletBalance, TransactionHistory, TransactionResponse,
    DailyLoginReward, ArticleReadReward, NewsShareReward, CommentReward,
    CouponCreate, CouponResponse, CouponRedeem, CouponRedemptionResponse,
    RewardSettingsCreate, RewardSettingsResponse, AdminWalletAdjustment,
    LeaderboardEntry, LeaderboardResponse, RewardsAnalytics, EngagementAnalytics
)

class RewardsService:
    """Service for managing rewards system"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_setting(self, key: str) -> int:
        """Get reward setting value"""
        setting = self.db.query(RewardSettings).filter(
            RewardSettings.setting_key == key,
            RewardSettings.is_active == True
        ).first()
        return setting.setting_value if setting else 0
    
    def initialize_default_settings(self):
        """Initialize default reward settings"""
        default_settings = [
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
        
        for key, value, description in default_settings:
            existing = self.db.query(RewardSettings).filter(RewardSettings.setting_key == key).first()
            if not existing:
                setting = RewardSettings(
                    setting_key=key,
                    setting_value=value,
                    description=description
                )
                self.db.add(setting)
        
        self.db.commit()
    
    def generate_referral_code(self, user_uid: str) -> str:
        """Generate unique referral code"""
        while True:
            code = secrets.token_hex(3).upper()  # 6-character code
            existing = self.db.query(UserReferral).filter(UserReferral.referral_code == code).first()
            if not existing:
                return code
    
    def create_user_wallet(self, user_uid: str) -> UserWallet:
        """Create wallet for new user"""
        wallet = UserWallet(user_uid=user_uid)
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet
    
    def get_user_wallet(self, user_uid: str) -> Optional[UserWallet]:
        """Get user wallet"""
        return self.db.query(UserWallet).filter(UserWallet.user_uid == user_uid).first()
    
    def get_or_create_wallet(self, user_uid: str) -> UserWallet:
        """Get or create user wallet"""
        wallet = self.get_user_wallet(user_uid)
        if not wallet:
            wallet = self.create_user_wallet(user_uid)
        return wallet
    
    def add_transaction(self, wallet_id: int, transaction_type: TransactionType, 
                       amount: int, description: str = None, reference_id: str = None) -> WalletTransaction:
        """Add transaction to wallet"""
        wallet = self.db.query(UserWallet).filter(UserWallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Update wallet balance
        wallet.current_balance += amount
        if amount > 0:
            wallet.total_earned += amount
        else:
            wallet.total_spent += abs(amount)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            reference_id=reference_id,
            balance_after=wallet.current_balance
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_wallet_balance(self, user_uid: str) -> WalletBalance:
        """Get wallet balance"""
        wallet = self.get_or_create_wallet(user_uid)
        return WalletBalance(
            current_balance=wallet.current_balance,
            total_earned=wallet.total_earned,
            total_spent=wallet.total_spent,
            daily_streak=wallet.daily_streak,
            longest_streak=wallet.longest_streak
        )
    
    def get_transaction_history(self, user_uid: str, page: int = 1, limit: int = 20) -> TransactionHistory:
        """Get transaction history"""
        wallet = self.get_or_create_wallet(user_uid)
        
        offset = (page - 1) * limit
        transactions = self.db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.id
        ).order_by(desc(WalletTransaction.created_at)).offset(offset).limit(limit).all()
        
        total = self.db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.id
        ).count()
        
        return TransactionHistory(
            transactions=[
                TransactionResponse(
                    id=t.id,
                    transaction_type=t.transaction_type.value,
                    amount=t.amount,
                    description=t.description,
                    reference_id=t.reference_id,
                    balance_after=t.balance_after,
                    created_at=t.created_at
                ) for t in transactions
            ],
            total_count=total,
            page=page,
            limit=limit
        )
    
    def process_referral_signup(self, user_uid: str, referral_code: str) -> ReferralVerificationResponse:
        """Process referral during signup"""
        referral = self.db.query(UserReferral).filter(
            UserReferral.referral_code == referral_code,
            UserReferral.status == ReferralStatus.PENDING
        ).first()
        
        if not referral:
            return ReferralVerificationResponse(
                success=False,
                message="Invalid or expired referral code"
            )
        
        # Check for fraud
        if self.detect_fraud(user_uid, referral.referrer_uid):
            return ReferralVerificationResponse(
                success=False,
                message="Referral verification failed due to suspicious activity"
            )
        
        # Update referral
        referral.referred_uid = user_uid
        referral.status = ReferralStatus.VERIFIED
        referral.verified_at = datetime.utcnow()
        
        # Create wallets if they don't exist
        referrer_wallet = self.get_or_create_wallet(referral.referrer_uid)
        referred_wallet = self.get_or_create_wallet(user_uid)
        
        return ReferralVerificationResponse(
            success=True,
            message="Referral verified! Complete OTP verification or first activity to earn rewards.",
            coins_awarded=0,  # Rewards given after verification/activity
            referrer_bonus=referral.reward_coins
        )
    
    def complete_referral_reward(self, user_uid: str, verification_method: str) -> ReferralVerificationResponse:
        """Complete referral reward after verification"""
        referral = self.db.query(UserReferral).filter(
            UserReferral.referred_uid == user_uid,
            UserReferral.status == ReferralStatus.VERIFIED,
            or_(
                UserReferral.referrer_reward_given == False,
                UserReferral.referred_reward_given == False
            )
        ).first()
        
        if not referral:
            return ReferralVerificationResponse(
                success=False,
                message="No pending referral rewards found"
            )
        
        referral.verification_method = verification_method
        referral.status = ReferralStatus.COMPLETED
        referral.completed_at = datetime.utcnow()
        
        coins_awarded = 0
        referrer_bonus = 0
        
        # Reward referred user
        if not referral.referred_reward_given:
            self.add_transaction(
                wallet_id=self.get_or_create_wallet(user_uid).id,
                transaction_type=TransactionType.WELCOME_BONUS,
                amount=referral.welcome_coins,
                description=f"Welcome bonus for referral signup",
                reference_id=referral.id
            )
            referral.referred_reward_given = True
            coins_awarded = referral.welcome_coins
        
        # Reward referrer
        if not referral.referrer_reward_given:
            self.add_transaction(
                wallet_id=self.get_or_create_wallet(referral.referrer_uid).id,
                transaction_type=TransactionType.REFERRAL_BONUS,
                amount=referral.reward_coins,
                description=f"Referral bonus for {user_uid}",
                reference_id=referral.id
            )
            referral.referrer_reward_given = True
            referrer_bonus = referral.reward_coins
        
        self.db.commit()
        
        return ReferralVerificationResponse(
            success=True,
            message="Referral rewards distributed successfully!",
            coins_awarded=coins_awarded,
            referrer_bonus=referrer_bonus
        )
    
    def process_daily_login(self, user_uid: str) -> DailyLoginReward:
        """Process daily login reward"""
        wallet = self.get_or_create_wallet(user_uid)
        today = datetime.utcnow().date()
        
        # Check if already logged in today
        if wallet.updated_at and wallet.updated_at.date() >= today:
            return DailyLoginReward(
                success=False,
                coins_awarded=0,
                daily_streak=wallet.daily_streak,
                message="Already received daily login reward today"
            )
        
        # Calculate streak
        yesterday = today - timedelta(days=1)
        if wallet.updated_at and wallet.updated_at.date() == yesterday:
            wallet.daily_streak += 1
        else:
            wallet.daily_streak = 1
        
        if wallet.daily_streak > wallet.longest_streak:
            wallet.longest_streak = wallet.daily_streak
        
        # Add login reward
        coins = self.get_setting("daily_login_coins")
        self.add_transaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.DAILY_LOGIN,
            amount=coins,
            description=f"Daily login reward - Streak: {wallet.daily_streak}",
            reference_id=str(wallet.daily_streak)
        )
        
        # Streak bonus
        streak_bonus = 0
        if wallet.daily_streak % 7 == 0:  # Weekly bonus
            streak_bonus = self.get_setting("streak_bonus_coins")
            self.add_transaction(
                wallet_id=wallet.id,
                transaction_type=TransactionType.STREAK_BONUS,
                amount=streak_bonus,
                description=f"Weekly streak bonus - Streak: {wallet.daily_streak}",
                reference_id=str(wallet.daily_streak)
            )
        
        wallet.updated_at = datetime.utcnow()
        self.db.commit()
        
        return DailyLoginReward(
            success=True,
            coins_awarded=coins + streak_bonus,
            daily_streak=wallet.daily_streak,
            message=f"Daily login reward earned! Current streak: {wallet.daily_streak}"
        )
    
    def process_article_read(self, user_uid: str, news_uid: str) -> ArticleReadReward:
        """Process article read reward"""
        today = datetime.utcnow().date()
        max_articles = self.get_setting("article_read_limit")
        coins_per_article = self.get_setting("article_read_coins")
        
        # Get or create daily engagement record
        engagement = self.db.query(DailyEngagement).filter(
            DailyEngagement.user_uid == user_uid,
            DailyEngagement.engagement_date >= today
        ).first()
        
        if not engagement:
            engagement = DailyEngagement(
                user_uid=user_uid,
                engagement_date=datetime.utcnow()
            )
            self.db.add(engagement)
        
        # Check limit
        if engagement.articles_read >= max_articles:
            return ArticleReadReward(
                success=False,
                coins_awarded=0,
                articles_read_today=engagement.articles_read,
                max_daily_limit=max_articles,
                message=f"Daily article read limit reached ({max_articles})"
            )
        
        # Check if already rewarded for this article
        existing = self.db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == self.get_or_create_wallet(user_uid).id,
            WalletTransaction.transaction_type == TransactionType.ARTICLE_READ,
            WalletTransaction.reference_id == news_uid
        ).first()
        
        if existing:
            return ArticleReadReward(
                success=False,
                coins_awarded=0,
                articles_read_today=engagement.articles_read,
                max_daily_limit=max_articles,
                message="Already rewarded for reading this article"
            )
        
        # Add reward
        self.add_transaction(
            wallet_id=self.get_or_create_wallet(user_uid).id,
            transaction_type=TransactionType.ARTICLE_READ,
            amount=coins_per_article,
            description=f"Article read reward",
            reference_id=news_uid
        )
        
        engagement.articles_read += 1
        engagement.total_coins_earned += coins_per_article
        self.db.commit()
        
        return ArticleReadReward(
            success=True,
            coins_awarded=coins_per_article,
            articles_read_today=engagement.articles_read,
            max_daily_limit=max_articles,
            message=f"Article read reward earned! ({engagement.articles_read}/{max_articles} today)"
        )
    
    def process_news_share(self, user_uid: str, news_uid: str, platform: str) -> NewsShareReward:
        """Process news share reward"""
        today = datetime.utcnow().date()
        max_shares = self.get_setting("news_share_limit")
        coins_per_share = self.get_setting("news_share_coins")
        
        # Get or create daily engagement record
        engagement = self.db.query(DailyEngagement).filter(
            DailyEngagement.user_uid == user_uid,
            DailyEngagement.engagement_date >= today
        ).first()
        
        if not engagement:
            engagement = DailyEngagement(
                user_uid=user_uid,
                engagement_date=datetime.utcnow()
            )
            self.db.add(engagement)
        
        # Check limit
        if engagement.news_shared >= max_shares:
            return NewsShareReward(
                success=False,
                coins_awarded=0,
                shares_today=engagement.news_shared,
                max_daily_limit=max_shares,
                message=f"Daily share limit reached ({max_shares})"
            )
        
        # Add reward
        self.add_transaction(
            wallet_id=self.get_or_create_wallet(user_uid).id,
            transaction_type=TransactionType.NEWS_SHARE,
            amount=coins_per_share,
            description=f"News share reward on {platform}",
            reference_id=f"{news_uid}_{platform}"
        )
        
        engagement.news_shared += 1
        engagement.total_coins_earned += coins_per_share
        self.db.commit()
        
        return NewsShareReward(
            success=True,
            coins_awarded=coins_per_share,
            shares_today=engagement.news_shared,
            max_daily_limit=max_shares,
            message=f"News share reward earned! ({engagement.news_shared}/{max_shares} today)"
        )
    
    def process_comment_reward(self, user_uid: str, comment_id: str) -> CommentReward:
        """Process comment reward"""
        today = datetime.utcnow().date()
        max_comments = self.get_setting("comment_limit")
        coins_per_comment = self.get_setting("comment_coins")
        
        # Get or create daily engagement record
        engagement = self.db.query(DailyEngagement).filter(
            DailyEngagement.user_uid == user_uid,
            DailyEngagement.engagement_date >= today
        ).first()
        
        if not engagement:
            engagement = DailyEngagement(
                user_uid=user_uid,
                engagement_date=datetime.utcnow()
            )
            self.db.add(engagement)
        
        # Check limit
        if engagement.comments_posted >= max_comments:
            return CommentReward(
                success=False,
                coins_awarded=0,
                comments_today=engagement.comments_posted,
                max_daily_limit=max_comments,
                message=f"Daily comment limit reached ({max_comments})"
            )
        
        # Add reward
        self.add_transaction(
            wallet_id=self.get_or_create_wallet(user_uid).id,
            transaction_type=TransactionType.COMMENT_POST,
            amount=coins_per_comment,
            description=f"Comment reward",
            reference_id=comment_id
        )
        
        engagement.comments_posted += 1
        engagement.total_coins_earned += coins_per_comment
        self.db.commit()
        
        return CommentReward(
            success=True,
            coins_awarded=coins_per_comment,
            comments_today=engagement.comments_posted,
            max_daily_limit=max_comments,
            message=f"Comment reward earned! ({engagement.comments_posted}/{max_comments} today)"
        )
    
    def detect_fraud(self, user_uid: str, referrer_uid: str) -> bool:
        """Detect fraudulent referral activity"""
        # Check IP/device patterns (simplified version)
        # In production, you'd check actual IP addresses and device fingerprints
        
        # Check if referrer has too many referrals from same device
        recent_referrals = self.db.query(UserReferral).filter(
            UserReferral.referrer_uid == referrer_uid,
            UserReferral.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        if recent_referrals > 10:  # More than 10 referrals in 24 hours
            return True
        
        return False
    
    def create_coupon(self, coupon_data: CouponCreate, admin_uid: str) -> CouponResponse:
        """Create new coupon"""
        coupon = Coupon(
            title=coupon_data.title,
            description=coupon_data.description,
            coin_cost=coupon_data.coin_cost,
            expiry_date=coupon_data.expiry_date,
            usage_limit=coupon_data.usage_limit,
            image_url=coupon_data.image_url,
            terms_conditions=coupon_data.terms_conditions,
            created_by=admin_uid
        )
        
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        
        return CouponResponse(
            id=coupon.id,
            title=coupon.title,
            description=coupon.description,
            coin_cost=coupon.coin_cost,
            expiry_date=coupon.expiry_date,
            usage_limit=coupon.usage_limit,
            usage_count=coupon.usage_count,
            status=coupon.status.value,
            image_url=coupon.image_url,
            terms_conditions=coupon.terms_conditions,
            is_available=True,
            created_at=coupon.created_at
        )
    
    def get_available_coupons(self, user_uid: str) -> List[CouponResponse]:
        """Get available coupons for user"""
        wallet = self.get_or_create_wallet(user_uid)
        now = datetime.utcnow()
        
        coupons = self.db.query(Coupon).filter(
            Coupon.status == "active",
            Coupon.expiry_date > now,
            or_(Coupon.usage_limit.is_(None), Coupon.usage_count < Coupon.usage_limit)
        ).all()
        
        available_coupons = []
        for coupon in coupons:
            is_available = wallet.current_balance >= coupon.coin_cost
            available_coupons.append(CouponResponse(
                id=coupon.id,
                title=coupon.title,
                description=coupon.description,
                coin_cost=coupon.coin_cost,
                expiry_date=coupon.expiry_date,
                usage_limit=coupon.usage_limit,
                usage_count=coupon.usage_count,
                status=coupon.status.value,
                image_url=coupon.image_url,
                terms_conditions=coupon.terms_conditions,
                is_available=is_available,
                created_at=coupon.created_at
            ))
        
        return available_coupons
    
    def redeem_coupon(self, user_uid: str, coupon_id: int) -> CouponRedemptionResponse:
        """Redeem coupon"""
        wallet = self.get_or_create_wallet(user_uid)
        coupon = self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
        
        if not coupon:
            return CouponRedemptionResponse(
                success=False,
                message="Coupon not found"
            )
        
        if coupon.status != "active":
            return CouponRedemptionResponse(
                success=False,
                message="Coupon is not active"
            )
        
        if coupon.expiry_date <= datetime.utcnow():
            return CouponRedemptionResponse(
                success=False,
                message="Coupon has expired"
            )
        
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return CouponRedemptionResponse(
                success=False,
                message="Coupon usage limit reached"
            )
        
        if wallet.current_balance < coupon.coin_cost:
            return CouponRedemptionResponse(
                success=False,
                message="Insufficient coins"
            )
        
        # Check if user already redeemed this coupon
        existing = self.db.query(CouponRedemption).filter(
            CouponRedemption.coupon_id == coupon_id,
            CouponRedemption.user_uid == user_uid
        ).first()
        
        if existing:
            return CouponRedemptionResponse(
                success=False,
                message="Coupon already redeemed"
            )
        
        # Process redemption
        redemption_code = secrets.token_hex(4).upper()
        
        # Deduct coins
        self.add_transaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.COUPON_REDEEM,
            amount=-coupon.coin_cost,
            description=f"Redeemed coupon: {coupon.title}",
            reference_id=str(coupon_id)
        )
        
        # Create redemption record
        redemption = CouponRedemption(
            coupon_id=coupon_id,
            user_uid=user_uid,
            coins_spent=coupon.coin_cost,
            redemption_code=redemption_code
        )
        
        self.db.add(redemption)
        
        # Update coupon usage count
        coupon.usage_count += 1
        
        self.db.commit()
        
        return CouponRedemptionResponse(
            success=True,
            message="Coupon redeemed successfully!",
            redemption_code=redemption_code,
            coins_spent=coupon.coin_cost,
            new_balance=wallet.current_balance
        )
    
    def get_leaderboard(self, limit: int = 50, user_uid: str = None) -> LeaderboardResponse:
        """Get leaderboard"""
        # Update leaderboard data
        self.update_leaderboard()
        
        # Get top users
        entries = self.db.query(Leaderboard).order_by(
            Leaderboard.rank_position.asc()
        ).limit(limit).all()
        
        leaderboard_entries = [
            LeaderboardEntry(
                user_uid=entry.user_uid,
                username=None,  # Would need to join with users table
                total_coins=entry.total_coins,
                referral_count=entry.referral_count,
                current_streak=entry.current_streak,
                rank_position=entry.rank_position
            ) for entry in entries
        ]
        
        user_rank = None
        if user_uid:
            user_entry = self.db.query(Leaderboard).filter(
                Leaderboard.user_uid == user_uid
            ).first()
            if user_entry:
                user_rank = LeaderboardEntry(
                    user_uid=user_entry.user_uid,
                    username=None,
                    total_coins=user_entry.total_coins,
                    referral_count=user_entry.referral_count,
                    current_streak=user_entry.current_streak,
                    rank_position=user_entry.rank_position
                )
        
        total_users = self.db.query(Leaderboard).count()
        
        return LeaderboardResponse(
            entries=leaderboard_entries,
            user_rank=user_rank,
            total_users=total_users
        )
    
    def update_leaderboard(self):
        """Update leaderboard data"""
        # Get all users with wallets
        users_with_coins = self.db.query(UserWallet).filter(
            UserWallet.total_earned > 0
        ).all()
        
        for wallet in users_with_coins:
            # Get referral count
            referral_count = self.db.query(UserReferral).filter(
                UserReferral.referrer_uid == wallet.user_uid,
                UserReferral.status == ReferralStatus.COMPLETED
            ).count()
            
            # Update or create leaderboard entry
            entry = self.db.query(Leaderboard).filter(
                Leaderboard.user_uid == wallet.user_uid
            ).first()
            
            if not entry:
                entry = Leaderboard(user_uid=wallet.user_uid)
                self.db.add(entry)
            
            entry.total_coins = wallet.total_earned
            entry.referral_count = referral_count
            entry.current_streak = wallet.daily_streak
            entry.last_updated = datetime.utcnow()
        
        # Update rankings
        all_entries = self.db.query(Leaderboard).order_by(
            desc(Leaderboard.total_coins),
            desc(Leaderboard.referral_count),
            desc(Leaderboard.current_streak)
        ).all()
        
        for i, entry in enumerate(all_entries, 1):
            entry.rank_position = i
        
        self.db.commit()
