from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.news import News, Reaction, Comment, Share, NewsView
from models.user import User
from schemas import (
    ReactionCreate, ReactionOut, ReactionResponse,
    CommentCreate, CommentUpdate, CommentOut, CommentResponse,
    ShareCreate, ShareOut, ShareResponse,
    ViewCreate, ViewOut, ViewResponse,
    EngagementStats
)

router = APIRouter()


# ==============================
# LIKE/REACTION ENDPOINTS
# ==============================

@router.post("/reactions", response_model=ReactionResponse, tags=["Engagement"])
def create_or_update_reaction(
    reaction: ReactionCreate,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Create or update a reaction (like) on news
    """
    # Check if news exists
    news = db.query(News).filter(News.news_uid == reaction.news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Check if user already reacted
    existing_reaction = db.query(Reaction).filter(
        Reaction.user_uid == user_uid,
        Reaction.news_uid == reaction.news_uid
    ).first()

    if existing_reaction:
        # Update existing reaction
        if existing_reaction.reaction_type == reaction.reaction_type:
            # Remove reaction if same type (toggle)
            db.delete(existing_reaction)
            db.commit()
            news.likes_count = max(0, news.likes_count - 1)
            db.commit()
            return ReactionResponse(
                message="Reaction removed",
                reaction=None,
                likes_count=news.likes_count
            )
        else:
            # Update reaction type
            existing_reaction.reaction_type = reaction.reaction_type
            db.commit()
            return ReactionResponse(
                message="Reaction updated",
                reaction=existing_reaction,
                likes_count=news.likes_count
            )
    else:
        # Create new reaction
        new_reaction = Reaction(
            user_uid=user_uid,
            news_uid=reaction.news_uid,
            reaction_type=reaction.reaction_type
        )
        db.add(new_reaction)
        news.likes_count += 1
        db.commit()
        db.refresh(new_reaction)
        return ReactionResponse(
            message="Reaction created",
            reaction=new_reaction,
            likes_count=news.likes_count
        )


@router.get("/reactions/{news_uid}", response_model=List[ReactionOut], tags=["Engagement"])
def get_news_reactions(
    news_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get all reactions for a news item
    """
    reactions = db.query(Reaction).filter(Reaction.news_uid == news_uid).all()
    return reactions


@router.get("/reactions/{news_uid}/user/{user_uid}", response_model=Optional[ReactionOut], tags=["Engagement"])
def get_user_reaction(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get user's reaction on a news item
    """
    reaction = db.query(Reaction).filter(
        Reaction.user_uid == user_uid,
        Reaction.news_uid == news_uid
    ).first()
    return reaction


@router.delete("/reactions/{news_uid}", response_model=ReactionResponse, tags=["Engagement"])
def delete_reaction(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Delete user's reaction on a news item
    """
    reaction = db.query(Reaction).filter(
        Reaction.user_uid == user_uid,
        Reaction.news_uid == news_uid
    ).first()

    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")

    news = db.query(News).filter(News.news_uid == news_uid).first()
    if news:
        news.likes_count = max(0, news.likes_count - 1)

    db.delete(reaction)
    db.commit()

    return ReactionResponse(
        message="Reaction deleted",
        reaction=None,
        likes_count=news.likes_count if news else 0
    )


# ==============================
# COMMENT ENDPOINTS
# ==============================

@router.post("/comments", response_model=CommentResponse, tags=["Engagement"])
def create_comment(
    comment: CommentCreate,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Create a comment on news
    """
    # Check if news exists
    news = db.query(News).filter(News.news_uid == comment.news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Create new comment
    new_comment = Comment(
        user_uid=user_uid,
        news_uid=comment.news_uid,
        comment_text=comment.comment_text
    )
    db.add(new_comment)
    news.comments_count += 1
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        message="Comment created",
        comment=new_comment,
        comments_count=news.comments_count
    )


@router.get("/comments/{news_uid}", response_model=List[CommentOut], tags=["Engagement"])
def get_news_comments(
    news_uid: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a news item
    """
    comments = db.query(Comment).filter(
        Comment.news_uid == news_uid
    ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    return comments


@router.get("/comments/{comment_id}", response_model=CommentOut, tags=["Engagement"])
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific comment by ID
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/comments/{comment_id}", response_model=CommentResponse, tags=["Engagement"])
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Update a comment (only by the comment owner)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_uid != user_uid:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment.comment_text = comment_update.comment_text
    db.commit()
    db.refresh(comment)

    news = db.query(News).filter(News.news_uid == comment.news_uid).first()

    return CommentResponse(
        message="Comment updated",
        comment=comment,
        comments_count=news.comments_count if news else 0
    )


@router.delete("/comments/{comment_id}", response_model=CommentResponse, tags=["Engagement"])
def delete_comment(
    comment_id: int,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a comment (only by the comment owner)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_uid != user_uid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    news_uid = comment.news_uid
    db.delete(comment)
    db.commit()

    news = db.query(News).filter(News.news_uid == news_uid).first()
    if news:
        news.comments_count = max(0, news.comments_count - 1)
        db.commit()

    return CommentResponse(
        message="Comment deleted",
        comment=None,
        comments_count=news.comments_count if news else 0
    )


# ==============================
# SHARE ENDPOINTS
# ==============================

@router.post("/shares", response_model=ShareResponse, tags=["Engagement"])
def create_share(
    share: ShareCreate,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Create a share record for news
    """
    # Check if news exists
    news = db.query(News).filter(News.news_uid == share.news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Check if user already shared (unique constraint)
    existing_share = db.query(Share).filter(
        Share.user_uid == user_uid,
        Share.news_uid == share.news_uid
    ).first()

    if existing_share:
        # Update platform if provided
        if share.platform:
            existing_share.platform = share.platform
            db.commit()
            db.refresh(existing_share)
        return ShareResponse(
            message="Already shared",
            share=existing_share,
            shares_count=news.shares_count
        )

    # Create new share
    new_share = Share(
        user_uid=user_uid,
        news_uid=share.news_uid,
        platform=share.platform
    )
    db.add(new_share)
    news.shares_count += 1
    db.commit()
    db.refresh(new_share)

    return ShareResponse(
        message="Share recorded",
        share=new_share,
        shares_count=news.shares_count
    )


@router.get("/shares/{news_uid}", response_model=List[ShareOut], tags=["Engagement"])
def get_news_shares(
    news_uid: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all shares for a news item
    """
    shares = db.query(Share).filter(
        Share.news_uid == news_uid
    ).order_by(Share.shared_at.desc()).offset(offset).limit(limit).all()
    return shares


@router.get("/shares/{news_uid}/user/{user_uid}", response_model=Optional[ShareOut], tags=["Engagement"])
def get_user_share(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    """
    Check if user has shared a news item
    """
    share = db.query(Share).filter(
        Share.user_uid == user_uid,
        Share.news_uid == news_uid
    ).first()
    return share


# ==============================
# VIEW ENDPOINTS
# ==============================

@router.post("/views", response_model=ViewResponse, tags=["Engagement"])
def create_view(
    view: ViewCreate,
    user_uid: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Record a view for news (user_uid optional for anonymous views)
    """
    # Check if news exists
    news = db.query(News).filter(News.news_uid == view.news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Create new view
    new_view = NewsView(
        news_uid=view.news_uid,
        user_uid=user_uid
    )
    db.add(new_view)
    news.views_count += 1
    db.commit()
    db.refresh(new_view)

    return ViewResponse(
        message="View recorded",
        view=new_view,
        views_count=news.views_count
    )


@router.get("/views/{news_uid}", response_model=List[ViewOut], tags=["Engagement"])
def get_news_views(
    news_uid: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all views for a news item
    """
    views = db.query(NewsView).filter(
        NewsView.news_uid == news_uid
    ).order_by(NewsView.viewed_at.desc()).offset(offset).limit(limit).all()
    return views


# ==============================
# ENGAGEMENT STATS ENDPOINT
# ==============================

@router.get("/stats/{news_uid}", response_model=EngagementStats, tags=["Engagement"])
def get_engagement_stats(
    news_uid: str,
    user_uid: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get engagement statistics for a news item
    """
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    user_reaction = None
    user_has_shared = False

    if user_uid:
        # Get user's reaction
        reaction = db.query(Reaction).filter(
            Reaction.user_uid == user_uid,
            Reaction.news_uid == news_uid
        ).first()
        if reaction:
            user_reaction = reaction.reaction_type

        # Check if user has shared
        share = db.query(Share).filter(
            Share.user_uid == user_uid,
            Share.news_uid == news_uid
        ).first()
        user_has_shared = share is not None

    return EngagementStats(
        news_uid=news_uid,
        likes_count=news.likes_count,
        comments_count=news.comments_count,
        shares_count=news.shares_count,
        views_count=news.views_count,
        user_reaction=user_reaction,
        user_has_shared=user_has_shared
    )
