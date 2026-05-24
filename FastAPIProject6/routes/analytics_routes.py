"""
Analytics Routes for Hyperlocal News Application
Comprehensive analytics and reporting dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from database import get_db
from models.news import News
from models.engagement import Bookmark, Notification
from models.user import User
from models.content import Advertisement, Event, Poll
from models.base_location import State, District, City
from auth.dependencies import admin_required, get_current_user
from models.user import User as UserModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_analytics_dashboard(
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(admin_required)
):
    """
    Get comprehensive analytics dashboard data
    """
    try:
        # Calculate time range
        time_mapping = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        start_date = datetime.utcnow() - time_mapping[time_range]
        
        # Get overall statistics
        total_news = db.query(News).filter(News.created_at >= start_date).count()
        approved_news = db.query(News).filter(
            and_(News.created_at >= start_date, News.is_approved == 1)
        ).count()
        
        total_users = db.query(User).filter(User.created_at >= start_date).count()
        active_users = db.query(User).filter(
            and_(User.created_at >= start_date, User.last_login >= start_date)
        ).count()
        
        # Engagement statistics
        total_views = db.query(func.sum(News.views_count)).filter(
            News.created_at >= start_date
        ).scalar() or 0
        
        total_likes = db.query(func.sum(News.likes_count)).filter(
            News.created_at >= start_date
        ).scalar() or 0
        
        total_comments = db.query(func.sum(News.comments_count)).filter(
            News.created_at >= start_date
        ).scalar() or 0
        
        total_shares = db.query(func.sum(News.shares_count)).filter(
            News.created_at >= start_date
        ).scalar() or 0
        
        # Top performing content
        top_news = db.query(News).filter(
            and_(News.created_at >= start_date, News.is_approved == 1)
        ).order_by(
            desc((News.views_count or 0) + (News.likes_count or 0) + (News.shares_count or 0))
        ).limit(5).all()
        
        # Category distribution
        category_stats = db.query(
            func.count(News.id).label('count'),
            func.sum(News.views_count).label('views')
        ).filter(
            and_(News.created_at >= start_date, News.is_approved == 1)
        ).group_by(News.category_id).all()
        
        # User growth over time
        user_growth = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date).group_by(
            func.date(User.created_at)
        ).order_by(func.date(User.created_at)).all()
        
        # Content creation trends
        content_trends = db.query(
            func.date(News.created_at).label('date'),
            func.count(News.id).label('count')
        ).filter(News.created_at >= start_date).group_by(
            func.date(News.created_at)
        ).order_by(func.date(News.created_at)).all()
        
        return {
            "success": True,
            "time_range": time_range,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "overview": {
                "total_news": total_news,
                "approved_news": approved_news,
                "approval_rate": round((approved_news / total_news * 100) if total_news > 0 else 0, 2),
                "total_users": total_users,
                "active_users": active_users,
                "user_activity_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
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
            "top_content": [
                {
                    "title": news.title,
                    "news_uid": news.news_uid,
                    "views": news.views_count or 0,
                    "likes": news.likes_count or 0,
                    "comments": news.comments_count or 0,
                    "shares": news.shares_count or 0,
                    "total_engagement": (news.views_count or 0) + (news.likes_count or 0) + (news.shares_count or 0)
                }
                for news in top_news
            ],
            "category_distribution": [
                {
                    "category_id": stat[0],
                    "count": stat[1] or 0,
                    "views": stat[2] or 0
                }
                for stat in category_stats
            ],
            "trends": {
                "user_growth": [
                    {"date": str(growth[0]), "count": growth[1]}
                    for growth in user_growth
                ],
                "content_creation": [
                    {"date": str(trend[0]), "count": trend[1]}
                    for trend in content_trends
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/content-performance")
def get_content_performance(
    content_type: str = Query("news", description="Content type: news, ads, events, polls"),
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    sort_by: str = Query("engagement", description="Sort by: engagement, views, likes, comments, shares"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(admin_required)
):
    """
    Get content performance analytics
    """
    try:
        # Calculate time range
        time_mapping = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        start_date = datetime.utcnow() - time_mapping[time_range]
        
        if content_type == "news":
            query = db.query(News).filter(
                and_(News.created_at >= start_date, News.is_approved == 1)
            )
            
            # Add sorting
            if sort_by == "views":
                query = query.order_by(desc(News.views_count))
            elif sort_by == "likes":
                query = query.order_by(desc(News.likes_count))
            elif sort_by == "comments":
                query = query.order_by(desc(News.comments_count))
            elif sort_by == "shares":
                query = query.order_by(desc(News.shares_count))
            else:  # engagement
                query = query.order_by(
                    desc((News.views_count or 0) + (News.likes_count or 0) + (News.shares_count or 0))
                )
            
            results = query.limit(limit).all()
            
            performance_data = []
            for item in results:
                performance_data.append({
                    "id": item.id,
                    "title": item.title,
                    "type": "news",
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "views": item.views_count or 0,
                    "likes": item.likes_count or 0,
                    "comments": item.comments_count or 0,
                    "shares": item.shares_count or 0,
                    "total_engagement": (item.views_count or 0) + (item.likes_count or 0) + (item.shares_count or 0),
                    "engagement_rate": round(
                        ((item.likes_count or 0) + (item.comments_count or 0) + (item.shares_count or 0)) / 
                        (item.views_count or 1) * 100, 2
                    )
                })
        
        elif content_type == "ads":
            query = db.query(Advertisement).filter(Advertisement.created_at >= start_date)
            results = query.limit(limit).all()
            
            performance_data = []
            for item in results:
                # Get ad impressions (you'd need to implement this)
                impressions = 0  # db.query(func.count(AdImpression.id)).filter(AdImpression.ad_id == item.id).scalar()
                performance_data.append({
                    "id": item.id,
                    "title": item.title,
                    "type": "advertisement",
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "impressions": impressions,
                    "clicks": 0,  # Would need click tracking
                    "ctr": round((0 / impressions * 100) if impressions > 0 else 0, 2)
                })
        
        else:
            # Handle other content types (events, polls)
            performance_data = []
        
        return {
            "success": True,
            "content_type": content_type,
            "time_range": time_range,
            "sort_by": sort_by,
            "data": performance_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content performance: {str(e)}")

@router.get("/user-analytics")
def get_user_analytics(
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(admin_required)
):
    """
    Get user behavior analytics
    """
    try:
        # Calculate time range
        time_mapping = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        start_date = datetime.utcnow() - time_mapping[time_range]
        
        # User registration trends
        registration_trends = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date).group_by(
            func.date(User.created_at)
        ).order_by(func.date(User.created_at)).all()
        
        # User activity by role
        users_by_role = db.query(
            User.role,
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date).group_by(User.role).all()
        
        # Most active users
        active_users = db.query(User).filter(
            User.last_login >= start_date
        ).order_by(desc(User.last_login)).limit(10).all()
        
        # User engagement
        total_bookmarks = db.query(Bookmark).filter(Bookmark.created_at >= start_date).count()
        total_notifications = db.query(Notification).filter(Notification.created_at >= start_date).count()
        
        return {
            "success": True,
            "time_range": time_range,
            "registration_trends": [
                {"date": str(trend[0]), "count": trend[1]}
                for trend in registration_trends
            ],
            "users_by_role": [
                {"role": role[0], "count": role[1]}
                for role in users_by_role
            ],
            "most_active_users": [
                {
                    "user_uid": user.user_uid,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in active_users
            ],
            "engagement_metrics": {
                "total_bookmarks": total_bookmarks,
                "total_notifications": total_notifications
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@router.get("/location-analytics")
def get_location_analytics(
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(admin_required)
):
    """
    Get location-based analytics
    """
    try:
        # Calculate time range
        time_mapping = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        start_date = datetime.utcnow() - time_mapping[time_range]
        
        # News by state
        news_by_state = db.query(
            State.name,
            func.count(News.id).label('count')
        ).join(City, News.city_id == City.id).join(
            District, City.district_id == District.id
        ).join(State, District.state_id == State.id).filter(
            and_(News.created_at >= start_date, News.is_approved == 1)
        ).group_by(State.name).order_by(desc(func.count(News.id))).all()
        
        # Users by state
        users_by_state = db.query(
            State.name,
            func.count(User.id).label('count')
        ).join(District, User.district_id == District.id).join(
            State, District.state_id == State.id
        ).filter(User.created_at >= start_date).group_by(State.name).order_by(
            desc(func.count(User.id))
        ).all()
        
        # Top cities by activity
        top_cities = db.query(
            City.name,
            State.name.label('state'),
            func.count(News.id).label('news_count'),
            func.count(User.id).label('user_count')
        ).join(District, City.district_id == District.id).join(
            State, District.state_id == State.id
        ).outerjoin(News, News.city_id == City.id).outerjoin(
            User, User.city_id == City.id
        ).filter(
            or_(News.created_at >= start_date, User.created_at >= start_date)
        ).group_by(City.id, State.name).order_by(
            desc(func.count(News.id) + func.count(User.id))
        ).limit(10).all()
        
        return {
            "success": True,
            "time_range": time_range,
            "news_by_state": [
                {"state": state[0], "count": state[1]}
                for state in news_by_state
            ],
            "users_by_state": [
                {"state": state[0], "count": state[1]}
                for state in users_by_state
            ],
            "top_cities": [
                {
                    "city": city[0],
                    "state": city[1],
                    "news_count": city[2],
                    "user_count": city[3],
                    "total_activity": city[2] + city[3]
                }
                for city in top_cities
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location analytics: {str(e)}")

@router.get("/reports/export")
def export_analytics_report(
    report_type: str = Query("dashboard", description="Report type: dashboard, content, users, locations"),
    format: str = Query("json", description="Export format: json, csv"),
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(admin_required)
):
    """
    Export analytics reports
    """
    try:
        # Get the appropriate data based on report type
        if report_type == "dashboard":
            data = get_analytics_dashboard(time_range, db, current_user)
        elif report_type == "content":
            data = get_content_performance("news", time_range, "engagement", 50, db, current_user)
        elif report_type == "users":
            data = get_user_analytics(time_range, db, current_user)
        elif report_type == "locations":
            data = get_location_analytics(time_range, db, current_user)
        else:
            raise HTTPException(status_code=400, detail="Invalid report_type")
        
        # Export in requested format
        if format == "json":
            return {
                "success": True,
                "report_type": report_type,
                "time_range": time_range,
                "exported_at": datetime.utcnow().isoformat(),
                "data": data
            }
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = convert_to_csv(data, report_type)
            return {
                "success": True,
                "report_type": report_type,
                "format": "csv",
                "data": csv_data
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")

def convert_to_csv(data: dict, report_type: str) -> str:
    """Convert analytics data to CSV format"""
    csv_lines = []
    
    if report_type == "dashboard":
        csv_lines.append("Metric,Value")
        overview = data.get("overview", {})
        for key, value in overview.items():
            csv_lines.append(f"{key},{value}")
    
    # Add more CSV conversion logic for other report types
    
    return "\n".join(csv_lines)
