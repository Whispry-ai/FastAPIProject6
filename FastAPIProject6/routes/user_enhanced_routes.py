"""
Enhanced User Routes for Hyperlocal News Application
Missing critical endpoints for user profiles and notifications
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

from database import get_db
from models.user import User
from models.engagement import Notification, Bookmark
from models.news import News
from auth.dependencies import get_current_user
from models.user import User as UserModel

router = APIRouter(prefix="/user", tags=["User Enhanced"])

# Pydantic models for request/response
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None

class UserResponse(BaseModel):
    user_uid: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    role: int
    language: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    email_verified: Optional[bool] = None
    mobile_verified: Optional[bool] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user's profile
    """
    return UserResponse(
        user_uid=current_user.user_uid,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        gender=current_user.gender,
        role=current_user.role,
        language=current_user.language,
        state_id=current_user.state_id,
        district_id=current_user.district_id,
        city_id=current_user.city_id,
        email_verified=current_user.email_verified,
        mobile_verified=current_user.mobile_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/profile")
def update_user_profile(
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    try:
        user = db.query(User).filter(User.user_uid == current_user.user_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if profile_update.name is not None:
            user.name = profile_update.name
        if profile_update.email is not None:
            # Check if email is already taken by another user
            existing_user = db.query(User).filter(
                and_(User.email == profile_update.email, User.user_uid != user.user_uid)
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = profile_update.email
            user.email_verified = False  # Reset verification
        if profile_update.date_of_birth is not None:
            try:
                dob = datetime.strptime(profile_update.date_of_birth, "%Y-%m-%d").date()
                user.date_of_birth = dob
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        if profile_update.gender is not None:
            if profile_update.gender not in ["male", "female", "other"]:
                raise HTTPException(status_code=400, detail="Invalid gender. Use: male, female, or other")
            user.gender = profile_update.gender
        
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": UserResponse(
                user_uid=user.user_uid,
                name=user.name,
                email=user.email,
                phone=user.phone,
                gender=user.gender,
                role=user.role,
                language=user.language,
                state_id=user.state_id,
                district_id=user.district_id,
                city_id=user.city_id,
                email_verified=user.email_verified,
                mobile_verified=user.mobile_verified,
                created_at=user.created_at,
                last_login=user.last_login
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/bookmarks")
def get_user_bookmarks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user's bookmarked news articles
    """
    try:
        # Get bookmarks with pagination
        offset = (page - 1) * limit
        
        bookmarks_query = db.query(Bookmark).filter(
            Bookmark.user_uid == current_user.user_uid
        ).order_by(desc(Bookmark.created_at))
        
        total = bookmarks_query.count()
        bookmarks = bookmarks_query.offset(offset).limit(limit).all()
        
        # Get news details for each bookmark
        bookmarked_news = []
        for bookmark in bookmarks:
            news = db.query(News).filter(News.news_uid == bookmark.news_uid).first()
            if news:
                bookmarked_news.append({
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
                    "bookmarked_at": bookmark.created_at.isoformat() if bookmark.created_at else None
                })
        
        return {
            "success": True,
            "bookmarks": bookmarked_news,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bookmarks: {str(e)}")

@router.get("/notifications")
def get_user_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user's notifications
    """
    try:
        # Build query
        query = db.query(Notification).filter(Notification.user_uid == current_user.user_uid)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Add pagination
        offset = (page - 1) * limit
        total = query.count()
        notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "notifications": [
                {
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                    "link_url": notif.link_url,
                    "notification_type": notif.notification_type,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at.isoformat() if notif.created_at else None
                }
                for notif in notifications
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1
            },
            "unread_count": db.query(Notification).filter(
                and_(
                    Notification.user_uid == current_user.user_uid,
                    Notification.is_read == False
                )
            ).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Mark notification as read
    """
    try:
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_uid == current_user.user_uid
            )
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.put("/notifications/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Mark all notifications as read
    """
    try:
        # Update all unread notifications
        db.query(Notification).filter(
            and_(
                Notification.user_uid == current_user.user_uid,
                Notification.is_read == False
            )
        ).update({"is_read": True})
        
        db.commit()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark all notifications as read: {str(e)}")

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete notification
    """
    try:
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_uid == current_user.user_uid
            )
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
        
        return {
            "success": True,
            "message": "Notification deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user's activity statistics
    """
    try:
        # User's news statistics
        user_news = db.query(News).filter(News.user_uid == current_user.user_uid).all()
        total_news = len(user_news)
        published_news = len([n for n in user_news if n.is_approved == 1])
        pending_news = total_news - published_news
        
        # Engagement statistics
        total_views = sum(n.views_count or 0 for n in user_news)
        total_likes = sum(n.likes_count or 0 for n in user_news)
        total_comments = sum(n.comments_count or 0 for n in user_news)
        total_shares = sum(n.shares_count or 0 for n in user_news)
        
        # Bookmark statistics
        bookmark_count = db.query(Bookmark).filter(
            Bookmark.user_uid == current_user.user_uid
        ).count()
        
        # Notification statistics
        total_notifications = db.query(Notification).filter(
            Notification.user_uid == current_user.user_uid
        ).count()
        unread_notifications = db.query(Notification).filter(
            and_(
                Notification.user_uid == current_user.user_uid,
                Notification.is_read == False
            )
        ).count()
        
        return {
            "success": True,
            "user_uid": current_user.user_uid,
            "news_stats": {
                "total_created": total_news,
                "published": published_news,
                "pending_approval": pending_news,
                "approval_rate": round((published_news / total_news * 100) if total_news > 0 else 0, 2)
            },
            "engagement_stats": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_engagement": total_views + total_likes + total_comments + total_shares
            },
            "activity_stats": {
                "bookmarks_count": bookmark_count,
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")
