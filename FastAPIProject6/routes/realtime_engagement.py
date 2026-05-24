"""
Real-time Engagement Routes for Hyperlocal News Application
Handles likes, comments, shares, and real-time engagement updates
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional
from datetime import datetime
import json

from database import get_db
from models.news import News, Reaction, Comment, Share, NewsView
from models.user import User
from models.engagement import Notification
from auth.dependencies import get_current_user
from websocket_manager import manager
from realtime_notifications import notification_service
from schemas import CommentCreate, ReactionCreate, ShareCreate

router = APIRouter()

@router.post("/realtime/like/{news_uid}")
async def like_news(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Like a news item and broadcast real-time update
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check if user already liked this news
    existing_like = db.query(Reaction).filter(
        and_(
            Reaction.news_uid == news_uid,
            Reaction.user_uid == current_user.user_uid,
            Reaction.reaction_type == 1  # 1 = like
        )
    ).first()
    
    if existing_like:
        # Unlike the news
        db.delete(existing_like)
        news.likes_count = max(0, (news.likes_count or 0) - 1)
        action = "unliked"
    else:
        # Like the news
        reaction = Reaction(
            news_uid=news_uid,
            user_uid=current_user.user_uid,
            reaction_type=1  # 1 = like
        )
        db.add(reaction)
        news.likes_count = (news.likes_count or 0) + 1
        action = "liked"
    
    db.commit()
    
    # Broadcast real-time engagement update
    engagement_data = {
        "type": "like_update",
        "news_uid": news_uid,
        "user_uid": current_user.user_uid,
        "action": action,
        "total_likes": news.likes_count,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_engagement_update(engagement_data)
    
    # Notify news author
    if action == "liked" and news.user_uid != current_user.user_uid:
        await notification_service.notify_engagement(
            "like", news_uid, current_user.user_uid, {
                "liker_name": current_user.name or current_user.user_name,
                "news_title": news.title
            }
        )
    
    return {
        "message": f"News {action} successfully",
        "news_uid": news_uid,
        "action": action,
        "total_likes": news.likes_count
    }

@router.post("/realtime/comment/{news_uid}")
async def comment_news(
    news_uid: str,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Comment on a news item and broadcast real-time update
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Create comment
    comment = Comment(
        news_uid=news_uid,
        user_uid=current_user.user_uid,
        content=comment_data.content,
        parent_id=comment_data.parent_id
    )
    db.add(comment)
    
    # Update comment count
    news.comments_count = (news.comments_count or 0) + 1
    
    db.commit()
    db.refresh(comment)
    
    # Get user info for broadcast
    commenter_info = {
        "user_uid": current_user.user_uid,
        "name": current_user.name or current_user.user_name,
        "avatar": None  # Add avatar field if available
    }
    
    # Broadcast real-time engagement update
    engagement_data = {
        "type": "comment_update",
        "news_uid": news_uid,
        "comment_id": comment.id,
        "user_uid": current_user.user_uid,
        "content": comment_data.content,
        "parent_id": comment_data.parent_id,
        "commenter": commenter_info,
        "total_comments": news.comments_count,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_engagement_update(engagement_data)
    
    # Notify news author
    if news.user_uid != current_user.user_uid:
        await notification_service.notify_engagement(
            "comment", news_uid, current_user.user_uid, {
                "commenter_name": current_user.name or current_user.user_name,
                "news_title": news.title,
                "comment_content": comment_data.content[:100]
            }
        )
    
    # Notify parent comment author (if reply)
    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if parent_comment and parent_comment.user_uid != current_user.user_uid:
            await notification_service.notify_engagement(
                "reply", news_uid, current_user.user_uid, {
                    "replier_name": current_user.name or current_user.user_name,
                    "news_title": news.title,
                    "reply_content": comment_data.content[:100]
                }
            )
    
    return {
        "message": "Comment added successfully",
        "comment_id": comment.id,
        "news_uid": news_uid,
        "total_comments": news.comments_count
    }

@router.post("/realtime/share/{news_uid}")
async def share_news(
    news_uid: str,
    share_data: ShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Share a news item and broadcast real-time update
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Create share record
    share = Share(
        news_uid=news_uid,
        user_uid=current_user.user_uid,
        platform=share_data.platform
    )
    db.add(share)
    
    # Update share count
    news.shares_count = (news.shares_count or 0) + 1
    
    db.commit()
    
    # Broadcast real-time engagement update
    engagement_data = {
        "type": "share_update",
        "news_uid": news_uid,
        "user_uid": current_user.user_uid,
        "platform": share_data.platform,
        "total_shares": news.shares_count,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_engagement_update(engagement_data)
    
    # Notify news author
    if news.user_uid != current_user.user_uid:
        await notification_service.notify_engagement(
            "share", news_uid, current_user.user_uid, {
                "sharer_name": current_user.name or current_user.user_name,
                "news_title": news.title,
                "platform": share_data.platform
            }
        )
    
    return {
        "message": "News shared successfully",
        "news_uid": news_uid,
        "platform": share_data.platform,
        "total_shares": news.shares_count
    }

@router.post("/realtime/view/{news_uid}")
async def track_news_view(
    news_uid: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track news view and update real-time metrics
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check if user already viewed this news recently (to prevent spam)
    recent_view = db.query(NewsView).filter(
        and_(
            NewsView.news_uid == news_uid,
            NewsView.user_uid == current_user.user_uid,
            NewsView.viewed_at >= datetime.utcnow() - timedelta(hours=1)
        )
    ).first()
    
    if not recent_view:
        # Create view record
        view = NewsView(
            news_uid=news_uid,
            user_uid=current_user.user_uid,
            session_id=session_id
        )
        db.add(view)
        
        # Update view count
        news.views_count = (news.views_count or 0) + 1
        
        db.commit()
        
        # Broadcast real-time view update (less frequent to avoid spam)
        if news.views_count % 10 == 0:  # Only broadcast every 10 views
            engagement_data = {
                "type": "view_update",
                "news_uid": news_uid,
                "total_views": news.views_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast_engagement_update(engagement_data)
    
    return {
        "message": "View tracked successfully",
        "news_uid": news_uid,
        "total_views": news.views_count
    }

@router.get("/realtime/comments/{news_uid}")
async def get_news_comments(
    news_uid: str,
    cursor: Optional[datetime] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get comments for a news item with real-time updates
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Build query
    query = db.query(Comment).filter(Comment.news_uid == news_uid)
    
    if cursor:
        query = query.filter(Comment.created_at < cursor)
    
    comments = query.order_by(desc(Comment.created_at)).limit(limit).all()
    
    # Format comments with user info
    comment_list = []
    for comment in comments:
        # Get user info
        user = db.query(User).filter(User.user_uid == comment.user_uid).first()
        
        # Get replies count
        replies_count = db.query(Comment).filter(
            Comment.parent_id == comment.id
        ).count()
        
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "parent_id": comment.parent_id,
            "user": {
                "user_uid": user.user_uid if user else comment.user_uid,
                "name": user.name if user else None,
                "user_name": user.user_name if user else None
            },
            "replies_count": replies_count,
            "created_at": comment.created_at.isoformat()
        }
        
        comment_list.append(comment_data)
    
    return {
        "news_uid": news_uid,
        "comments": comment_list,
        "total_comments": news.comments_count or 0,
        "has_more": len(comment_list) == limit,
        "next_cursor": comment_list[-1]["created_at"] if comment_list else None
    }

@router.get("/realtime/engagement/{news_uid}")
async def get_engagement_metrics(
    news_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get real-time engagement metrics for a news item
    """
    
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Get detailed engagement metrics
    total_views = db.query(NewsView).filter(
        NewsView.news_uid == news_uid
    ).count()
    
    total_likes = db.query(Reaction).filter(
        and_(Reaction.news_uid == news_uid, Reaction.reaction_type == 1)
    ).count()
    
    total_comments = db.query(Comment).filter(
        Comment.news_uid == news_uid
    ).count()
    
    total_shares = db.query(Share).filter(
        Share.news_uid == news_uid
    ).count()
    
    # Get engagement over time (last 24 hours)
    since_time = datetime.utcnow() - timedelta(hours=24)
    
    views_24h = db.query(NewsView).filter(
        and_(
            NewsView.news_uid == news_uid,
            NewsView.viewed_at >= since_time
        )
    ).count()
    
    likes_24h = db.query(Reaction).filter(
        and_(
            Reaction.news_uid == news_uid,
            Reaction.reaction_type == 1,
            Reaction.created_at >= since_time
        )
    ).count()
    
    return {
        "news_uid": news_uid,
        "total_engagement": {
            "views": total_views,
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares
        },
        "last_24_hours": {
            "views": views_24h,
            "likes": likes_24h,
            "engagement_rate": round((likes_24h / max(views_24h, 1)) * 100, 2)
        },
        "updated_at": datetime.utcnow().isoformat()
    }
