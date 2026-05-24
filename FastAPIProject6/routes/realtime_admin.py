"""
Real-time Admin Dashboard Routes for Hyperlocal News Application
Provides live content management, analytics, and system monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
import asyncio

from database import get_db
from models.news import News, Category, NewsView, Reaction, Comment, Share
from models.user import User, UserPreference
from models.content import SponsoredPost, Advertisement
from models.engagement import Notification
from auth.dependencies import get_current_user, require_role
from schemas import UserRole
from websocket_manager import manager

router = APIRouter()

@router.get("/realtime/admin/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EMPLOYEE))
):
    """
    Get real-time admin dashboard data
    Includes live statistics, recent activities, and system health
    """
    
    # Time ranges for analytics
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    # Basic statistics
    total_users = db.query(User).count()
    total_news = db.query(News).count()
    total_categories = db.query(Category).count()
    
    # News statistics
    published_news = db.query(News).filter(News.is_approved == 1).count()
    pending_news = db.query(News).filter(News.is_approved == 0).count()
    breaking_news = db.query(News).filter(
        and_(
            News.is_breaking == True,
            News.breaking_expires_at > now
        )
    ).count()
    
    # User activity (last 24h)
    active_users_24h = db.query(User).filter(
        User.last_login >= last_24h
    ).count()
    
    new_users_24h = db.query(User).filter(
        User.created_at >= last_24h
    ).count()
    
    # News activity (last 24h)
    news_published_24h = db.query(News).filter(
        and_(
            News.is_approved == 1,
            News.created_at >= last_24h
        )
    ).count()
    
    # Engagement metrics (last 24h)
    views_24h = db.query(NewsView).filter(
        NewsView.viewed_at >= last_24h
    ).count()
    
    likes_24h = db.query(Reaction).filter(
        and_(
            Reaction.reaction_type == 1,
            Reaction.created_at >= last_24h
        )
    ).count()
    
    comments_24h = db.query(Comment).filter(
        Comment.created_at >= last_24h
    ).count()
    
    # Top performing news (last 7 days)
    top_news = db.query(News).filter(
        and_(
            News.is_approved == 1,
            News.created_at >= last_7d
        )
    ).order_by(
        desc((News.likes_count + News.comments_count + News.shares_count + News.views_count))
    ).limit(10).all()
    
    # Recent activities
    recent_news = db.query(News).order_by(
        desc(News.created_at)
    ).limit(5).all()
    
    recent_users = db.query(User).order_by(
        desc(User.created_at)
    ).limit(5).all()
    
    # System health
    websocket_connections = manager.get_connection_stats()
    
    return {
        "dashboard_stats": {
            "users": {
                "total": total_users,
                "active_24h": active_users_24h,
                "new_24h": new_users_24h
            },
            "news": {
                "total": total_news,
                "published": published_news,
                "pending": pending_news,
                "breaking": breaking_news,
                "published_24h": news_published_24h
            },
            "categories": total_categories,
            "engagement_24h": {
                "views": views_24h,
                "likes": likes_24h,
                "comments": comments_24h
            }
        },
        "top_news": [
            {
                "news_uid": news.news_uid,
                "title": news.title,
                "total_engagement": (news.likes_count or 0) + (news.comments_count or 0) + \
                                  (news.shares_count or 0) + (news.views_count or 0),
                "created_at": news.created_at.isoformat()
            }
            for news in top_news
        ],
        "recent_activities": {
            "news": [
                {
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "status": "published" if news.is_approved else "pending",
                    "created_at": news.created_at.isoformat()
                }
                for news in recent_news
            ],
            "users": [
                {
                    "user_uid": user.user_uid,
                    "name": user.name or user.user_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat()
                }
                for user in recent_users
            ]
        },
        "system_health": {
            "websocket_connections": websocket_connections,
            "server_time": now.isoformat(),
            "database_status": "healthy"  # Add actual DB health check
        },
        "updated_at": now.isoformat()
    }

@router.get("/realtime/admin/pending-news")
async def get_pending_news(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER))
):
    """
    Get pending news for approval with real-time updates
    """
    
    pending_news = db.query(News).filter(
        News.is_approved == 0
    ).order_by(desc(News.created_at)).limit(limit).all()
    
    return {
        "pending_count": db.query(News).filter(News.is_approved == 0).count(),
        "items": [
            {
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "user_uid": news.user_uid,
                "created_at": news.created_at.isoformat(),
                "image_url": news.image_url
            }
            for news in pending_news
        ],
        "updated_at": datetime.utcnow().isoformat()
    }

@router.post("/realtime/admin/approve-news/{news_uid}")
async def approve_news_realtime(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER))
):
    """
    Approve news and broadcast real-time update
    """
    
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.is_approved == 1:
        return {"message": "News already approved"}
    
    # Approve news
    news.is_approved = 1
    news.approved_by_uid = current_user.user_uid
    news.approved_at = datetime.utcnow()
    
    db.commit()
    
    # Broadcast approval to all connected users
    await manager.broadcast_news_update({
        "type": "news_approved",
        "news_uid": news_uid,
        "title": news.title,
        "summary": news.summary,
        "image_url": news.image_url,
        "approved_by": current_user.name or current_user.user_name,
        "approved_at": news.approved_at.isoformat()
    })
    
    return {
        "message": "News approved and broadcasted",
        "news_uid": news_uid,
        "approved_by": current_user.user_uid
    }

@router.get("/realtime/admin/analytics")
async def get_realtime_analytics(
    time_range: str = "24h",  # 24h, 7d, 30d
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EMPLOYEE))
):
    """
    Get real-time analytics and metrics
    """
    
    # Calculate time range
    now = datetime.utcnow()
    if time_range == "24h":
        since = now - timedelta(hours=24)
    elif time_range == "7d":
        since = now - timedelta(days=7)
    elif time_range == "30d":
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(hours=24)
    
    # News analytics
    news_stats = db.query(
        func.count(News.id).label('total'),
        func.sum(News.views_count).label('total_views'),
        func.sum(News.likes_count).label('total_likes'),
        func.sum(News.comments_count).label('total_comments'),
        func.sum(News.shares_count).label('total_shares')
    ).filter(
        and_(
            News.is_approved == 1,
            News.created_at >= since
        )
    ).first()
    
    # User analytics
    user_stats = db.query(
        func.count(User.id).label('new_users'),
        func.count(User.id).filter(User.last_login >= since).label('active_users')
    ).filter(User.created_at >= since).first()
    
    # Engagement trends (hourly for last 24h)
    if time_range == "24h":
        engagement_trends = []
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            hourly_stats = db.query(
                func.count(NewsView.id).label('views'),
                func.count(Reaction.id).label('likes'),
                func.count(Comment.id).label('comments')
            ).filter(
                or_(
                    NewsView.viewed_at.between(hour_start, hour_end),
                    Reaction.created_at.between(hour_start, hour_end),
                    Comment.created_at.between(hour_start, hour_end)
                )
            ).first()
            
            engagement_trends.append({
                "hour": hour_start.strftime("%H:00"),
                "views": hourly_stats.views or 0,
                "likes": hourly_stats.likes or 0,
                "comments": hourly_stats.comments or 0
            })
        
        engagement_trends.reverse()  # Chronological order
    else:
        engagement_trends = []
    
    # Top categories
    category_stats = db.query(
        Category.name,
        func.count(News.id).label('news_count')
    ).join(
        News.categories
    ).filter(
        and_(
            News.is_approved == 1,
            News.created_at >= since
        )
    ).group_by(Category.id, Category.name).order_by(
        desc('news_count')
    ).limit(10).all()
    
    return {
        "time_range": time_range,
        "period": {
            "start": since.isoformat(),
            "end": now.isoformat()
        },
        "news_analytics": {
            "total_published": news_stats.total or 0,
            "total_views": news_stats.total_views or 0,
            "total_likes": news_stats.total_likes or 0,
            "total_comments": news_stats.total_comments or 0,
            "total_shares": news_stats.total_shares or 0
        },
        "user_analytics": {
            "new_users": user_stats.new_users or 0,
            "active_users": user_stats.active_users or 0
        },
        "engagement_trends": engagement_trends,
        "top_categories": [
            {
                "name": stat.name,
                "news_count": stat.news_count
            }
            for stat in category_stats
        ],
        "updated_at": now.isoformat()
    }

@router.websocket("/realtime/admin/ws/{user_uid}")
async def admin_websocket(
    websocket: WebSocket,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket for real-time admin dashboard updates
    """
    
    # Verify admin user
    user = db.query(User).filter(
        and_(
            User.user_uid == user_uid,
            User.role.in_([3, 4, 5])  # EMPLOYEE, PUBLISHER, ADMIN
        )
    ).first()
    
    if not user:
        await websocket.close(code(4003), reason="Admin access required")
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Send periodic dashboard updates
            dashboard_data = await get_admin_dashboard(db, user)
            await websocket.send_text(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            # Wait before next update (30 seconds)
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason="Internal server error")

@router.post("/realtime/admin/broadcast")
async def admin_broadcast(
    message_data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Broadcast admin message to all users
    Only accessible by admins
    """
    
    broadcast_message = {
        "type": "admin_broadcast",
        "title": message_data.get("title", "Admin Announcement"),
        "message": message_data.get("message"),
        "priority": message_data.get("priority", "high"),
        "sender": current_user.name or current_user.user_name,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Broadcast to all connected users
    await manager.broadcast_to_all(broadcast_message)
    
    # Store as notification for all users
    # (This would be implemented based on your notification system)
    
    return {
        "message": "Admin broadcast sent successfully",
        "timestamp": datetime.utcnow().isoformat()
    }
