from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models.news import News, Reaction, Comment, Share, NewsView
from models.user import User
from auth.dependencies import get_current_user

router = APIRouter(tags=["Engagement"])

# Pydantic Models
class ReactionCreate(BaseModel):
    reaction_type: str = "like"  # like, love, laugh, angry, sad
    news_uid: str
    user_uid: str

class CommentCreate(BaseModel):
    content: str
    news_uid: str
    user_uid: str
    parent_id: Optional[int] = None

class ShareCreate(BaseModel):
    platform: str  # facebook, twitter, whatsapp, linkedin, etc.
    news_uid: str
    user_uid: str

class ViewCreate(BaseModel):
    news_uid: str
    user_uid: Optional[str] = None

# Likes/Reactions Endpoints
@router.post("/like")
def like_news(reaction_data: ReactionCreate, db: Session = Depends(get_db)):
    """Like or unlike a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == reaction_data.news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Check if user already reacted
        existing_reaction = db.query(Reaction).filter(
            Reaction.news_uid == reaction_data.news_uid,
            Reaction.user_uid == reaction_data.user_uid
        ).first()
        
        if existing_reaction:
            # Remove reaction (unlike)
            db.delete(existing_reaction)
            action = "unliked"
        else:
            # Add new reaction
            reaction_type_map = {"like": 1, "love": 2, "laugh": 3, "angry": 4, "sad": 5}
            reaction_int = reaction_type_map.get(reaction_data.reaction_type, 1)
            
            new_reaction = Reaction(
                news_uid=reaction_data.news_uid,
                user_uid=reaction_data.user_uid,
                reaction_type=reaction_int
            )
            db.add(new_reaction)
            action = "liked"
        
        # Update news like count
        like_count = db.query(Reaction).filter(
            Reaction.news_uid == reaction_data.news_uid,
            Reaction.reaction_type == 1  # 1 = like
        ).count()
        
        news.likes_count = like_count
        db.commit()
        
        return {
            "success": True,
            "message": f"News {action} successfully",
            "likes_count": like_count,
            "action": action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process like: {str(e)}")

@router.get("/like/{news_uid}")
def get_like_status(news_uid: str, user_uid: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Get like status for a news article"""
    try:
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Get total likes
        total_likes = db.query(Reaction).filter(
            Reaction.news_uid == news_uid,
            Reaction.reaction_type == "like"
        ).count()
        
        # Check if user liked
        user_liked = False
        if user_uid:
            user_reaction = db.query(Reaction).filter(
                Reaction.news_uid == news_uid,
                Reaction.user_uid == user_uid,
                Reaction.reaction_type == "like"
            ).first()
            user_liked = bool(user_reaction)
        
        return {
            "success": True,
            "total_likes": total_likes,
            "user_liked": user_liked,
            "likes_count": news.likes_count or 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get like status: {str(e)}")

# Comments Endpoints
@router.post("/comment")
def add_comment(comment_data: CommentCreate, db: Session = Depends(get_db)):
    """Add a comment to a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == comment_data.news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Create new comment
        new_comment = Comment(
            news_uid=comment_data.news_uid,
            user_uid=comment_data.user_uid,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
            commented_at=datetime.utcnow()
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Update news comment count
        comment_count = db.query(Comment).filter(
            Comment.news_uid == comment_data.news_uid
        ).count()
        
        news.comments_count = comment_count
        db.commit()
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment_id": new_comment.id,
            "comments_count": comment_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")

@router.get("/comments/{news_uid}")
def get_comments(
    news_uid: str, 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get comments for a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Get comments with pagination
        offset = (page - 1) * limit
        comments = db.query(Comment).filter(
            Comment.news_uid == news_uid
        ).order_by(desc(Comment.commented_at)).offset(offset).limit(limit).all()
        
        # Format comments
        comments_data = []
        for comment in comments:
            comments_data.append({
                "id": comment.id,
                "content": comment.content,
                "user_uid": comment.user_uid,
                "parent_id": comment.parent_id,
                "commented_at": comment.commented_at.isoformat(),
                "replies_count": db.query(Comment).filter(Comment.parent_id == comment.id).count()
            })
        
        # Get total count
        total_comments = db.query(Comment).filter(
            Comment.news_uid == news_uid
        ).count()
        
        return {
            "success": True,
            "comments": comments_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_comments,
                "pages": (total_comments + limit - 1) // limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

@router.delete("/comment/{comment_id}")
def delete_comment(comment_id: int, user_uid: str, db: Session = Depends(get_db)):
    """Delete a comment (only by the comment author)"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.user_uid != user_uid:
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
        db.delete(comment)
        db.commit()
        
        # Update news comment count
        comment_count = db.query(Comment).filter(
            Comment.news_uid == comment.news_uid
        ).count()
        
        news = db.query(News).filter(News.news_uid == comment.news_uid).first()
        if news:
            news.comments_count = comment_count
            db.commit()
        
        return {
            "success": True,
            "message": "Comment deleted successfully",
            "comments_count": comment_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

# View Tracking Endpoints
@router.post("/view/{news_uid}")
def record_view(news_uid: str, view_data: ViewCreate, db: Session = Depends(get_db)):
    """Record a view for a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Check if user viewed recently (rate limiting - 1 hour)
        if view_data.user_uid:
            recent_view = db.query(NewsView).filter(
                NewsView.news_uid == news_uid,
                NewsView.user_uid == view_data.user_uid,
                NewsView.viewed_at >= datetime.utcnow() - timedelta(hours=1)
            ).first()
            
            if recent_view:
                return {
                    "success": True,
                    "message": "View already recorded recently",
                    "views_count": news.views_count or 0
                }
        
        # Create new view record
        new_view = NewsView(
            news_uid=news_uid,
            user_uid=view_data.user_uid,
            viewed_at=datetime.utcnow()
        )
        
        db.add(new_view)
        db.commit()
        
        # Update news view count
        view_count = db.query(NewsView).filter(NewsView.news_uid == news_uid).count()
        news.views_count = view_count
        db.commit()
        
        return {
            "success": True,
            "message": "View recorded successfully",
            "views_count": view_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record view: {str(e)}")

@router.post("/view/anonymous/{news_uid}")
def record_anonymous_view(news_uid: str, db: Session = Depends(get_db)):
    """Record an anonymous view for a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Create anonymous view record
        new_view = NewsView(
            news_uid=news_uid,
            user_uid=None,  # Anonymous
            viewed_at=datetime.utcnow()
        )
        
        db.add(new_view)
        db.commit()
        
        # Update news view count
        view_count = db.query(NewsView).filter(NewsView.news_uid == news_uid).count()
        news.views_count = view_count
        db.commit()
        
        return {
            "success": True,
            "message": "Anonymous view recorded successfully",
            "views_count": view_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record anonymous view: {str(e)}")

# Share Tracking Endpoints
@router.post("/share")
def record_share(share_data: ShareCreate, db: Session = Depends(get_db)):
    """Record a share for a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == share_data.news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Create new share record
        new_share = Share(
            news_uid=share_data.news_uid,
            user_uid=share_data.user_uid,
            platform=share_data.platform,
            shared_at=datetime.utcnow()
        )
        
        db.add(new_share)
        db.commit()
        
        # Update news share count
        share_count = db.query(Share).filter(Share.news_uid == share_data.news_uid).count()
        news.shares_count = share_count
        db.commit()
        
        return {
            "success": True,
            "message": f"Share recorded successfully on {share_data.platform}",
            "shares_count": share_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record share: {str(e)}")

# Statistics Endpoints
@router.get("/stats/{news_uid}")
def get_engagement_stats(news_uid: str, user_uid: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Get engagement statistics for a news article"""
    try:
        # Check if news exists
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Get all engagement stats
        stats = {
            "news_uid": news_uid,
            "views_count": news.views_count or 0,
            "likes_count": news.likes_count or 0,
            "shares_count": news.shares_count or 0,
            "comments_count": news.comments_count or 0,
            "total_interactions": (news.views_count or 0) + (news.likes_count or 0) + (news.shares_count or 0) + (news.comments_count or 0)
        }
        
        # Add user-specific stats if user_uid provided
        if user_uid:
            user_stats = {
                "user_liked": bool(db.query(Reaction).filter(
                    Reaction.news_uid == news_uid,
                    Reaction.user_uid == user_uid,
                    Reaction.reaction_type == "like"
                ).first()),
                "user_commented": bool(db.query(Comment).filter(
                    Comment.news_uid == news_uid,
                    Comment.user_uid == user_uid
                ).first()),
                "user_shared": bool(db.query(Share).filter(
                    Share.news_uid == news_uid,
                    Share.user_uid == user_uid
                ).first()),
                "user_viewed": bool(db.query(NewsView).filter(
                    NewsView.news_uid == news_uid,
                    NewsView.user_uid == user_uid
                ).first())
            }
            stats["user_stats"] = user_stats
        
        return {
            "success": True,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/stats/public/{news_uid}")
def get_public_engagement_stats(news_uid: str, db: Session = Depends(get_db)):
    """Get public engagement statistics (no user data)"""
    try:
        news = db.query(News).filter(News.news_uid == news_uid).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        return {
            "success": True,
            "stats": {
                "views_count": news.views_count or 0,
                "likes_count": news.likes_count or 0,
                "shares_count": news.shares_count or 0,
                "comments_count": news.comments_count or 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get public stats: {str(e)}")

@router.get("/top-engaged")
def get_top_engaged_news(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get top engaged news articles"""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get top news by total engagement
        top_news = db.query(News).filter(
            News.is_approved == 1,
            News.created_at >= start_date
        ).order_by(
            desc(
                (News.views_count or 0) + 
                (News.likes_count or 0) + 
                (News.shares_count or 0) + 
                (News.comments_count or 0)
            )
        ).limit(limit).all()
        
        news_data = []
        for news in top_news:
            total_engagement = (news.views_count or 0) + (news.likes_count or 0) + (news.shares_count or 0) + (news.comments_count or 0)
            news_data.append({
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "views_count": news.views_count or 0,
                "likes_count": news.likes_count or 0,
                "shares_count": news.shares_count or 0,
                "comments_count": news.comments_count or 0,
                "total_engagement": total_engagement,
                "created_at": news.created_at.isoformat() if news.created_at else None
            })
        
        return {
            "success": True,
            "news": news_data,
            "period": f"Last {days} days",
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top engaged news: {str(e)}")
