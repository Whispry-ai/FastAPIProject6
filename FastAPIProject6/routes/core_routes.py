"""
Core Routes for Hyperlocal News Application
Essential endpoints for health, stats, and basic functionality
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any
from datetime import datetime, timedelta
import sys

from database import get_db
from models.news import News
from models.user import User
from models.engagement import Notification
from auth.dependencies import get_current_user
from models.user import User as UserModel

router = APIRouter(tags=["Core"])

@router.get("/health")
def health_check():
    """
    Health check endpoint to verify application status
    """
    try:
        # Basic health metrics
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "system": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform
            },
            "uptime": "running"
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/stats")
def get_application_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get application statistics
    """
    try:
        # Time ranges
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # User statistics
        total_users = db.query(User).count()
        active_users_24h = db.query(User).filter(User.last_login >= last_24h).count()
        active_users_7d = db.query(User).filter(User.last_login >= last_7d).count()
        
        # News statistics
        total_news = db.query(News).count()
        published_news = db.query(News).filter(News.is_approved == 1).count()
        news_24h = db.query(News).filter(News.created_at >= last_24h).count()
        news_7d = db.query(News).filter(News.created_at >= last_7d).count()
        
        # Engagement statistics
        total_views = db.query(func.sum(News.views_count)).scalar() or 0
        total_likes = db.query(func.sum(News.likes_count)).scalar() or 0
        total_comments = db.query(func.sum(News.comments_count)).scalar() or 0
        total_shares = db.query(func.sum(News.shares_count)).scalar() or 0
        
        # Notification statistics
        total_notifications = db.query(Notification).count()
        unread_notifications = db.query(Notification).filter(
            Notification.is_read == False
        ).count()
        
        return {
            "success": True,
            "timestamp": now.isoformat(),
            "users": {
                "total": total_users,
                "active_24h": active_users_24h,
                "active_7d": active_users_7d,
                "activity_rate": round((active_users_7d / total_users * 100) if total_users > 0 else 0, 2)
            },
            "news": {
                "total": total_news,
                "published": published_news,
                "pending_approval": total_news - published_news,
                "created_24h": news_24h,
                "created_7d": news_7d,
                "approval_rate": round((published_news / total_news * 100) if total_news > 0 else 0, 2)
            },
            "engagement": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "engagement_rate": round(
                    ((total_likes + total_comments + total_shares) / total_views * 100) 
                    if total_views > 0 else 0, 2
                )
            },
            "notifications": {
                "total": total_notifications,
                "unread": unread_notifications
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/info")
def get_application_info():
    """
    Get application information
    """
    return {
        "name": "Hyperlocal News API",
        "version": "1.0.0",
        "description": "AI-powered hyperlocal news platform with real-time updates",
        "features": [
            "News creation and publishing",
            "User authentication and roles",
            "AI content analysis",
            "Location-based content",
            "Real-time notifications",
            "Analytics dashboard",
            "File upload system",
            "Search functionality",
            "Admin moderation tools"
        ],
        "endpoints_count": "40+",
        "database": "PostgreSQL",
        "framework": "FastAPI",
        "ai_integration": "Google Gemini API",
        "supported_languages": ["English", "Telugu", "Hindi"],
        "location_coverage": ["Maharashtra", "Delhi", "Karnataka", "Andhra Pradesh", "Telangana", "Tamil Nadu"],
        "created_at": "2024",
        "status": "production_ready"
    }
