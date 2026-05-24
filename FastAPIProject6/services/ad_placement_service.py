"""
Advanced Ad Placement Service for Hyperlocal News Application
Intelligent ad targeting and placement algorithm
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import math

from models.content import Advertisement
from models.user import User
from models.news import News
from models.content import AdImpression
from database import get_db

class AdPlacementService:
    """Service for intelligent ad placement and targeting"""
    
    def __init__(self):
        self.default_placement_interval = 3  # Insert ad every 3 news articles
        self.max_ads_per_feed = 5  # Maximum ads in a single feed
        self.ad_types = {
            "premium": {"priority": 10, "weight": 0.3},
            "standard": {"priority": 5, "weight": 0.5},
            "basic": {"priority": 1, "weight": 0.2}
        }
    
    def get_targeted_ads(
        self, 
        user: User, 
        db: Session,
        limit: int = 10,
        exclude_seen: bool = True
    ) -> List[Advertisement]:
        """
        Get targeted advertisements based on user profile and preferences
        """
        try:
            # Build base query for active ads
            now = datetime.utcnow()
            query = db.query(Advertisement).filter(
                and_(
                    Advertisement.is_approved == True,
                    Advertisement.start_date <= now,
                    Advertisement.end_date >= now
                )
            )
            
            # Location targeting
            if user.city_id:
                query = query.filter(Advertisement.city_id == user.city_id)
            elif user.district_id:
                query = query.filter(Advertisement.district_id == user.district_id)
            elif user.state_id:
                query = query.filter(Advertisement.state_id == user.state_id)
            
            # Demographic targeting
            if user.gender:
                query = query.filter(
                    or_(
                        Advertisement.target_gender == user.gender,
                        Advertisement.target_gender == "all"
                    )
                )
            
            if user.date_of_birth:
                age = self.calculate_age(user.date_of_birth)
                query = query.filter(
                    and_(
                        Advertisement.target_age_min <= age,
                        Advertisement.target_age_max >= age
                    )
                )
            
            # Exclude already seen ads if requested
            if exclude_seen:
                seen_ad_ids = self.get_seen_ad_ids(user.user_uid, db)
                if seen_ad_ids:
                    query = query.filter(~Advertisement.id.in_(seen_ad_ids))
            
            # Order by priority and relevance score
            ads = query.order_by(
                desc(Advertisement.priority),
                desc(Advertisement.created_at)
            ).limit(limit * 2).all()  # Get more to allow for filtering
            
            # Calculate relevance scores and sort
            scored_ads = []
            for ad in ads:
                relevance_score = self.calculate_ad_relevance(ad, user)
                scored_ads.append({
                    "ad": ad,
                    "score": relevance_score
                })
            
            # Sort by relevance score and return top results
            scored_ads.sort(key=lambda x: x["score"], reverse=True)
            return [item["ad"] for item in scored_ads[:limit]]
            
        except Exception as e:
            print(f"Error getting targeted ads: {e}")
            return []
    
    def calculate_ad_relevance(self, ad: Advertisement, user: User) -> float:
        """
        Calculate relevance score for ad targeting
        """
        score = 0.0
        
        # Location relevance (40% weight)
        if user.city_id and ad.city_id == user.city_id:
            score += 0.4
        elif user.district_id and ad.district_id == user.district_id:
            score += 0.3
        elif user.state_id and ad.state_id == user.state_id:
            score += 0.2
        
        # Demographic relevance (30% weight)
        if user.gender:
            if ad.target_gender == user.gender:
                score += 0.15
            elif ad.target_gender == "all":
                score += 0.1
        
        if user.date_of_birth:
            age = self.calculate_age(user.date_of_birth)
            if ad.target_age_min <= age <= ad.target_age_max:
                score += 0.15
        
        # Priority relevance (20% weight)
        if ad.priority:
            score += min(ad.priority / 10, 0.2)
        
        # Performance relevance (10% weight)
        # This would use actual performance data in production
        score += 0.1
        
        return min(score, 1.0)
    
    def place_ads_in_feed(
        self, 
        news_items: List[Dict], 
        user: User, 
        db: Session,
        placement_interval: Optional[int] = None,
        max_ads: Optional[int] = None
    ) -> List[Dict]:
        """
        Insert advertisements into news feed with intelligent placement
        """
        try:
            if not news_items:
                return []
            
            placement_interval = placement_interval or self.default_placement_interval
            max_ads = max_ads or self.max_ads_per_feed
            
            # Get targeted ads
            targeted_ads = self.get_targeted_ads(user, db, limit=max_ads)
            
            if not targeted_ads:
                return news_items
            
            # Calculate optimal placement positions
            feed_length = len(news_items)
            max_positions = min(feed_length // placement_interval, max_ads)
            
            # Generate placement positions
            positions = []
            for i in range(max_positions):
                position = (i + 1) * placement_interval - 1  # 2, 5, 8, etc.
                if position < feed_length:
                    positions.append(position)
            
            # Insert ads at calculated positions
            enhanced_feed = []
            ad_index = 0
            
            for i, news_item in enumerate(news_items):
                # Add news item
                enhanced_feed.append(news_item)
                
                # Check if we should insert an ad
                if i in positions and ad_index < len(targeted_ads):
                    ad = targeted_ads[ad_index]
                    
                    # Create ad item
                    ad_item = {
                        "type": "advertisement",
                        "id": ad.id,
                        "title": ad.title,
                        "content": ad.content,
                        "image_url": ad.image_url,
                        "cta_text": ad.cta_text,
                        "cta_url": ad.cta_url,
                        "placement_type": "in_feed",
                        "position": i + 1,
                        "relevance_score": self.calculate_ad_relevance(ad, user),
                        "priority": ad.priority,
                        "targeting": {
                            "location": {
                                "state_id": ad.state_id,
                                "district_id": ad.district_id,
                                "city_id": ad.city_id
                            },
                            "demographics": {
                                "target_gender": ad.target_gender,
                                "target_age_range": f"{ad.target_age_min}-{ad.target_age_max}"
                            }
                        }
                    }
                    
                    enhanced_feed.append(ad_item)
                    ad_index += 1
                    
                    # Log impression
                    self.log_ad_impression(ad.id, user.user_uid, db)
            
            return enhanced_feed
            
        except Exception as e:
            print(f"Error placing ads in feed: {e}")
            return news_items
    
    def log_ad_impression(self, ad_id: int, user_uid: str, db: Session):
        """
        Log ad impression for analytics
        """
        try:
            impression = AdImpression(
                ad_id=ad_id,
                user_uid=user_uid,
                impression_at=datetime.utcnow(),
                ip_address=None  # Would be populated from request
            )
            db.add(impression)
            db.commit()
        except Exception as e:
            print(f"Error logging ad impression: {e}")
    
    def get_seen_ad_ids(self, user_uid: str, db: Session, days_back: int = 7) -> List[int]:
        """
        Get IDs of ads user has seen recently
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            impressions = db.query(AdImpression.ad_id).filter(
                and_(
                    AdImpression.user_uid == user_uid,
                    AdImpression.impression_at >= cutoff_date
                )
            ).distinct().all()
            
            return [imp[0] for imp in impressions]
        except Exception as e:
            print(f"Error getting seen ad IDs: {e}")
            return []
    
    def calculate_age(self, date_of_birth) -> int:
        """
        Calculate age from date of birth
        """
        try:
            if isinstance(date_of_birth, str):
                date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            
            today = datetime.utcnow().date()
            age = today.year - date_of_birth.year
            
            # Adjust if birthday hasn't occurred this year yet
            if today.month < date_of_birth.month or (
                today.month == date_of_birth.month and today.day < date_of_birth.day
            ):
                age -= 1
            
            return age
        except:
            return 25  # Default age if calculation fails
    
    def get_ad_performance_analytics(
        self, 
        ad_id: int, 
        db: Session,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance analytics for a specific ad
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get impressions
            impressions = db.query(AdImpression).filter(
                and_(
                    AdImpression.ad_id == ad_id,
                    AdImpression.impression_at >= cutoff_date
                )
            ).all()
            
            # Calculate metrics
            total_impressions = len(impressions)
            unique_users = len(set(imp.user_uid for imp in impressions))
            
            # Daily breakdown
            daily_impressions = {}
            for imp in impressions:
                date_key = imp.impression_at.strftime("%Y-%m-%d")
                daily_impressions[date_key] = daily_impressions.get(date_key, 0) + 1
            
            return {
                "ad_id": ad_id,
                "period_days": days_back,
                "total_impressions": total_impressions,
                "unique_users": unique_users,
                "avg_impressions_per_user": round(
                    total_impressions / unique_users, 2
                ) if unique_users > 0 else 0,
                "daily_breakdown": daily_impressions,
                "impressions_per_day": round(total_impressions / days_back, 2)
            }
            
        except Exception as e:
            print(f"Error getting ad performance: {e}")
            return {}
    
    def optimize_ad_placement(
        self, 
        user: User, 
        db: Session,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Optimize ad placement strategy based on user behavior and context
        """
        try:
            context = context or {}
            
            # Get user's engagement patterns
            recent_impressions = self.get_seen_ad_ids(user.user_uid, db, days_back=1)
            
            # Determine optimal placement strategy
            strategy = {
                "placement_interval": self.default_placement_interval,
                "max_ads": self.max_ads_per_feed,
                "ad_types": ["premium", "standard", "basic"],
                "targeting_weights": {
                    "location": 0.4,
                    "demographics": 0.3,
                    "behavior": 0.2,
                    "performance": 0.1
                }
            }
            
            # Adjust based on user behavior
            if len(recent_impressions) > 10:  # Heavy user - reduce ads
                strategy["placement_interval"] = 4
                strategy["max_ads"] = 3
            elif len(recent_impressions) < 2:  # Light user - can show more
                strategy["placement_interval"] = 2
                strategy["max_ads"] = 6
            
            # Adjust based on time of day
            current_hour = datetime.utcnow().hour
            if 9 <= current_hour <= 17:  # Business hours
                strategy["ad_types"] = ["premium", "standard"]
            else:  # Personal time
                strategy["ad_types"] = ["standard", "basic"]
            
            return {
                "success": True,
                "strategy": strategy,
                "user_uid": user.user_uid,
                "context": context
            }
            
        except Exception as e:
            print(f"Error optimizing ad placement: {e}")
            return {"success": False, "error": str(e)}

# Global ad placement service instance
ad_placement_service = AdPlacementService()
