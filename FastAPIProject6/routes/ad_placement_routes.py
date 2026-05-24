"""
Ad Placement Routes for Hyperlocal News Application
Advanced ad targeting and placement API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from services.ad_placement_service import ad_placement_service
from auth.dependencies import get_current_user
from models.user import User as UserModel
from models.news import News

router = APIRouter(prefix="/ads", tags=["Ad Placement"])

# Pydantic models
class AdPlacementRequest(BaseModel):
    placement_interval: Optional[int] = None
    max_ads: Optional[int] = None
    exclude_seen: Optional[bool] = True

class AdTestRequest(BaseModel):
    user_uid: str
    news_count: int = 20
    placement_interval: Optional[int] = None
    max_ads: Optional[int] = None

@router.get("/targeted")
def get_targeted_ads(
    limit: int = Query(10, ge=1, le=50, description="Number of ads to return"),
    exclude_seen: bool = Query(True, description="Exclude already seen ads"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get targeted advertisements for the current user
    """
    try:
        ads = ad_placement_service.get_targeted_ads(
            user=current_user,
            db=db,
            limit=limit,
            exclude_seen=exclude_seen
        )
        
        return {
            "success": True,
            "user_uid": current_user.user_uid,
            "ads": [
                {
                    "id": ad.id,
                    "title": ad.title,
                    "content": ad.content,
                    "image_url": ad.image_url,
                    "cta_text": ad.cta_text,
                    "cta_url": ad.cta_url,
                    "priority": ad.priority,
                    "relevance_score": ad_placement_service.calculate_ad_relevance(ad, current_user),
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
                    },
                    "schedule": {
                        "start_date": ad.start_date.isoformat() if ad.start_date else None,
                        "end_date": ad.end_date.isoformat() if ad.end_date else None,
                        "is_active": (
                            ad.start_date <= datetime.utcnow() <= ad.end_date
                            if ad.start_date and ad.end_date else False
                        )
                    }
                }
                for ad in ads
            ],
            "total_count": len(ads),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get targeted ads: {str(e)}")

@router.post("/placement-test")
def test_ad_placement(
    request: AdTestRequest,
    db: Session = Depends(get_db)
):
    """
    Test ad placement with simulated user and news
    """
    try:
        # Get or create test user
        from models.user import User
        test_user = db.query(User).filter(User.user_uid == request.user_uid).first()
        if not test_user:
            # Create a test user for demonstration
            test_user = User(
                user_uid="test123",  # 8 characters max
                name="Test User",
                email="test@example.com",
                role=2,  # USER role
                state_id=1  # Default state
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        # Get sample news items
        news_items = db.query(News).filter(News.is_approved == 1).limit(request.news_count).all()
        
        # Convert to feed format
        news_feed = [
            {
                "type": "news",
                "id": news.id,
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "created_at": news.created_at.isoformat() if news.created_at else None,
                "views_count": news.views_count or 0,
                "likes_count": news.likes_count or 0,
                "comments_count": news.comments_count or 0,
                "shares_count": news.shares_count or 0
            }
            for news in news_items
        ]
        
        # Apply ad placement
        enhanced_feed = ad_placement_service.place_ads_in_feed(
            news_items=news_feed,
            user=test_user,
            db=db,
            placement_interval=request.placement_interval,
            max_ads=request.max_ads
        )
        
        # Analyze placement results
        news_count = len([item for item in enhanced_feed if item.get("type") == "news"])
        ad_count = len([item for item in enhanced_feed if item.get("type") == "advertisement"])
        
        return {
            "success": True,
            "test_user": {
                "user_uid": test_user.user_uid,
                "name": test_user.name,
                "location": {
                    "state_id": test_user.state_id,
                    "district_id": test_user.district_id,
                    "city_id": test_user.city_id
                },
                "demographics": {
                    "gender": test_user.gender,
                    "age": ad_placement_service.calculate_age(test_user.date_of_birth) if test_user.date_of_birth else None
                }
            },
            "placement_config": {
                "placement_interval": request.placement_interval or ad_placement_service.default_placement_interval,
                "max_ads": request.max_ads or ad_placement_service.max_ads_per_feed
            },
            "results": {
                "total_items": len(enhanced_feed),
                "news_items": news_count,
                "ad_items": ad_count,
                "ad_ratio": round((ad_count / len(enhanced_feed)) * 100, 2) if enhanced_feed else 0
            },
            "feed_preview": enhanced_feed[:10],  # Show first 10 items
            "placement_positions": [
                {
                    "position": i,
                    "type": item.get("type"),
                    "title": item.get("title", "")[:50] + "..." if len(item.get("title", "")) > 50 else item.get("title", "")
                }
                for i, item in enumerate(enhanced_feed)
                if item.get("type") == "advertisement"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ad placement test failed: {str(e)}")

@router.get("/performance/{ad_id}")
def get_ad_performance(
    ad_id: int,
    days_back: int = Query(30, ge=1, le=90, description="Days of analytics to show"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get performance analytics for a specific advertisement
    """
    try:
        # Check if user owns this ad or is admin
        from models.content import Advertisement
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        
        if not ad:
            raise HTTPException(status_code=404, detail="Advertisement not found")
        
        # Check permissions (admin or ad owner)
        if current_user.role != 5 and ad.user_uid != current_user.user_uid:  # 5 = admin
            raise HTTPException(status_code=403, detail="Permission denied")
        
        performance = ad_placement_service.get_ad_performance_analytics(
            ad_id=ad_id,
            db=db,
            days_back=days_back
        )
        
        return {
            "success": True,
            "ad_id": ad_id,
            "ad_title": ad.title,
            "period_days": days_back,
            "performance": performance,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ad performance: {str(e)}")

@router.get("/strategy/optimize")
def get_optimized_placement_strategy(
    context: Optional[str] = Query(None, description="Context for optimization (e.g., 'business_hours', 'weekend')"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get optimized ad placement strategy for current user
    """
    try:
        context_data = {}
        if context:
            context_data["context"] = context
        
        optimization = ad_placement_service.optimize_ad_placement(
            user=current_user,
            db=db,
            context=context_data
        )
        
        return {
            "success": True,
            "user_uid": current_user.user_uid,
            "optimization": optimization,
            "current_time": datetime.utcnow().isoformat(),
            "recommendations": {
                "best_placement_interval": optimization.get("strategy", {}).get("placement_interval"),
                "recommended_max_ads": optimization.get("strategy", {}).get("max_ads"),
                "optimal_ad_types": optimization.get("strategy", {}).get("ad_types"),
                "targeting_weights": optimization.get("strategy", {}).get("targeting_weights")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize placement: {str(e)}")

@router.get("/analytics/overview")
def get_ad_analytics_overview(
    days_back: int = Query(7, ge=1, le=90, description="Days of analytics to show"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get comprehensive ad analytics overview
    """
    try:
        # Get user's ads or all ads if admin
        from models.content import Advertisement
        from models.engagement import AdImpression
        
        if current_user.role == 5:  # Admin
            ads_query = db.query(Advertisement).filter(Advertisement.is_approved == True)
        else:
            ads_query = db.query(Advertisement).filter(
                and_(
                    Advertisement.user_uid == current_user.user_uid,
                    Advertisement.is_approved == True
                )
            )
        
        ads = ads_query.all()
        
        # Calculate analytics for each ad
        analytics = []
        total_impressions = 0
        total_unique_users = 0
        
        for ad in ads:
            ad_performance = ad_placement_service.get_ad_performance_analytics(
                ad_id=ad.id,
                db=db,
                days_back=days_back
            )
            
            if ad_performance:
                analytics.append({
                    "ad_id": ad.id,
                    "ad_title": ad.title,
                    "impressions": ad_performance.get("total_impressions", 0),
                    "unique_users": ad_performance.get("unique_users", 0),
                    "avg_impressions_per_user": ad_performance.get("avg_impressions_per_user", 0),
                    "impressions_per_day": ad_performance.get("impressions_per_day", 0)
                })
                
                total_impressions += ad_performance.get("total_impressions", 0)
                total_unique_users += ad_performance.get("unique_users", 0)
        
        # Sort by impressions
        analytics.sort(key=lambda x: x["impressions"], reverse=True)
        
        return {
            "success": True,
            "period_days": days_back,
            "summary": {
                "total_ads": len(ads),
                "total_impressions": total_impressions,
                "total_unique_users": total_unique_users,
                "avg_impressions_per_ad": round(total_impressions / len(ads), 2) if ads else 0,
                "avg_impressions_per_day": round(total_impressions / days_back, 2)
            },
            "top_performing_ads": analytics[:5],
            "all_ads_analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/config")
def get_ad_placement_config():
    """
    Get current ad placement configuration
    """
    return {
        "success": True,
        "config": {
            "default_placement_interval": ad_placement_service.default_placement_interval,
            "max_ads_per_feed": ad_placement_service.max_ads_per_feed,
            "ad_types": ad_placement_service.ad_types,
            "targeting_weights": {
                "location": 0.4,
                "demographics": 0.3,
                "behavior": 0.2,
                "performance": 0.1
            }
        },
        "placement_logic": {
            "description": "Ads are inserted after every N news articles",
            "example": "With interval=3: News, News, News, AD, News, News, News, AD...",
            "max_protection": f"Maximum {ad_placement_service.max_ads_per_feed} ads per feed",
            "smart_targeting": "Location, demographics, and behavior-based targeting"
        }
    }
