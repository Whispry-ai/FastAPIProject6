"""
Enhanced News Routes for Hyperlocal News Application
Missing critical endpoints for complete news functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models.news import News, Category
from models.engagement import Bookmark
from auth.dependencies import get_current_user
from models.user import User as UserModel

router = APIRouter(prefix="/news", tags=["News Enhanced"])

@router.get("/")
def get_all_news(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all published news articles
    """
    try:
        # Get approved news
        news_query = db.query(News).filter(News.is_approved == 1)
        
        # Count total
        total = news_query.count()
        
        # Add pagination
        offset = (page - 1) * limit
        news_items = news_query.order_by(desc(News.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        news_data = []
        for news in news_items:
            news_data.append({
                "id": news.id,
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "views_count": news.views_count or 0,
                "likes_count": news.likes_count or 0,
                "shares_count": news.shares_count or 0,
                "comments_count": news.comments_count or 0,
                "created_at": news.created_at.isoformat() if news.created_at else None,
                "language_id": news.language_id,
                "city_id": news.city_id,
                "is_approved": news.is_approved,
                "is_auto_generated": news.is_auto_generated
            })
        
        return {
            "success": True,
            "news": news_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get news: {str(e)}")

@router.get("/categories")
def get_news_categories(
    db: Session = Depends(get_db)
):
    """
    Get all available news categories
    """
    try:
        categories = db.query(Category).all()
        
        return {
            "success": True,
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "description": getattr(cat, 'description', ''),
                    "news_count": db.query(News).filter(
                        and_(News.is_approved == 1, News.categories.any(id=cat.id))
                    ).count()
                }
                for cat in categories
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/trending")
def get_trending_news(
    time_range: str = Query("24h", description="Time range: 1h, 6h, 24h, 7d"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Get trending news based on engagement
    """
    try:
        # Calculate time range
        time_mapping = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        start_date = datetime.utcnow() - time_mapping[time_range]
        
        # Get trending news
        trending_news = db.query(News).filter(
            and_(
                News.is_approved == 1,
                News.created_at >= start_date
            )
        ).order_by(
            desc(
                (News.views_count or 0) + 
                (News.likes_count or 0) + 
                (News.shares_count or 0) + 
                (News.comments_count or 0)
            )
        ).limit(limit).all()
        
        return {
            "success": True,
            "time_range": time_range,
            "trending_news": [
                {
                    "id": news.id,
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "summary": news.summary,
                    "image_url": news.image_url,
                    "created_at": news.created_at.isoformat() if news.created_at else None,
                    "views_count": news.views_count or 0,
                    "likes_count": news.likes_count or 0,
                    "comments_count": news.comments_count or 0,
                    "shares_count": news.shares_count or 0,
                    "trending_score": (
                        (news.views_count or 0) + 
                        (news.likes_count or 0) + 
                        (news.shares_count or 0) + 
                        (news.comments_count or 0)
                    ),
                    "is_breaking": news.is_breaking or False
                }
                for news in trending_news
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending news: {str(e)}")

@router.get("/recommended")
def get_recommended_news(
    user_uid: str = Query(..., description="User UID for personalization"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get recommended news for user based on preferences and activity
    """
    try:
        # Get user preferences
        user = db.query(UserModel).filter(UserModel.user_uid == user_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build recommendation query
        query = db.query(News).filter(News.is_approved == 1)
        
        # Filter by user's preferred location if available
        if user.city_id:
            query = query.filter(News.city_id == user.city_id)
        elif user.district_id:
            # Get cities in user's district
            from models.base_location import City
            cities_in_district = db.query(City.id).filter(City.district_id == user.district_id).all()
            city_ids = [city[0] for city in cities_in_district]
            query = query.filter(News.city_id.in_(city_ids))
        
        # Filter by user's preferred language if available
        if user.language_id:
            query = query.filter(News.language_id == user.language_id)
        
        # Get recent and popular news
        recent_date = datetime.utcnow() - timedelta(days=7)
        query = query.filter(News.created_at >= recent_date)
        
        # Order by engagement and recency
        recommended_news = query.order_by(
            desc(
                (News.views_count or 0) + 
                (News.likes_count or 0) + 
                (News.shares_count or 0)
            ),
            desc(News.created_at)
        ).limit(limit).all()
        
        return {
            "success": True,
            "user_uid": user_uid,
            "recommendations": [
                {
                    "id": news.id,
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "summary": news.summary,
                    "image_url": news.image_url,
                    "created_at": news.created_at.isoformat() if news.created_at else None,
                    "views_count": news.views_count or 0,
                    "likes_count": news.likes_count or 0,
                    "comments_count": news.comments_count or 0,
                    "shares_count": news.shares_count or 0,
                    "relevance_score": calculate_relevance_score(news, user)
                }
                for news in recommended_news
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/{news_uid}/bookmark")
def bookmark_news(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Bookmark a news article
    """
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Check if already bookmarked
        existing_bookmark = db.query(Bookmark).filter(
            and_(
                Bookmark.user_uid == current_user.user_uid,
                Bookmark.news_uid == news_uid
            )
        ).first()
        
        if existing_bookmark:
            raise HTTPException(status_code=400, detail="News already bookmarked")
        
        # Create bookmark
        bookmark = Bookmark(
            user_uid=current_user.user_uid,
            news_uid=news_uid
        )
        db.add(bookmark)
        db.commit()
        
        return {
            "success": True,
            "message": "News bookmarked successfully",
            "bookmark": {
                "news_uid": news_uid,
                "user_uid": current_user.user_uid,
                "created_at": bookmark.created_at.isoformat() if bookmark.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bookmark news: {str(e)}")

@router.delete("/{news_uid}/bookmark")
def remove_bookmark(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Remove bookmark from news article
    """
    try:
        # Find and delete bookmark
        bookmark = db.query(Bookmark).filter(
            and_(
                Bookmark.user_uid == current_user.user_uid,
                Bookmark.news_uid == news_uid
            )
        ).first()
        
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        db.delete(bookmark)
        db.commit()
        
        return {
            "success": True,
            "message": "Bookmark removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove bookmark: {str(e)}")

@router.post("/{news_uid}/report")
def report_news(
    news_uid: str,
    reason: str = Query(..., description="Reason for reporting"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Report inappropriate content
    """
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Create report (you might want to create a NewsReport model)
        # For now, we'll use the existing flagged_content system
        
        # Check if already reported
        from models.content import FlaggedContent
        existing_report = db.query(FlaggedContent).filter(
            and_(
                FlaggedContent.user_uid == current_user.user_uid,
                FlaggedContent.news_uid == news_uid
            )
        ).first()
        
        if existing_report:
            raise HTTPException(status_code=400, detail="News already reported")
        
        # Create report
        report = FlaggedContent(
            user_uid=current_user.user_uid,
            news_uid=news_uid,
            reason=reason,
            status="pending"
        )
        db.add(report)
        db.commit()
        
        return {
            "success": True,
            "message": "News reported successfully",
            "report": {
                "news_uid": news_uid,
                "reason": reason,
                "status": "pending",
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to report news: {str(e)}")

def calculate_relevance_score(news: News, user: UserModel) -> float:
    """Calculate relevance score for news recommendation"""
    score = 0.0
    
    # Location relevance
    if user.city_id and news.city_id == user.city_id:
        score += 0.4
    elif user.district_id and news.city and news.city.district_id == user.district_id:
        score += 0.2
    
    # Language relevance
    if user.language_id and news.language_id == user.language_id:
        score += 0.3
    
    # Recency relevance
    if news.created_at:
        days_old = (datetime.utcnow() - news.created_at).days
        if days_old <= 1:
            score += 0.2
        elif days_old <= 7:
            score += 0.1
    
    # Engagement relevance
    engagement = (news.views_count or 0) + (news.likes_count or 0)
    if engagement > 100:
        score += 0.1
    
    return min(score, 1.0)
