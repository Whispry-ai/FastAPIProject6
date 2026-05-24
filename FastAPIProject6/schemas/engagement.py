from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ==============================
# LIKE/REACTION SCHEMAS
# ==============================

class ReactionCreate(BaseModel):
    news_uid: str = Field(..., description="News UID to react to")
    reaction_type: int = Field(..., description="Reaction type (1=like, 2=love, 3=haha, 4=wow, 5=sad, 6=angry)")


class ReactionOut(BaseModel):
    id: int
    user_uid: str
    news_uid: str
    reaction_type: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionResponse(BaseModel):
    message: str
    reaction: Optional[ReactionOut] = None
    likes_count: int


# ==============================
# COMMENT SCHEMAS
# ==============================

class CommentCreate(BaseModel):
    news_uid: str = Field(..., description="News UID to comment on")
    comment_text: str = Field(..., min_length=1, max_length=1000, description="Comment text")


class CommentUpdate(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=1000, description="Updated comment text")


class CommentOut(BaseModel):
    id: int
    user_uid: str
    news_uid: str
    comment_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    message: str
    comment: Optional[CommentOut] = None
    comments_count: int


# ==============================
# SHARE SCHEMAS
# ==============================

class ShareCreate(BaseModel):
    news_uid: str = Field(..., description="News UID to share")
    platform: Optional[str] = Field(None, description="Platform shared on (e.g., 'whatsapp', 'facebook', 'twitter')")


class ShareOut(BaseModel):
    id: int
    news_uid: str
    user_uid: str
    shared_at: datetime
    platform: Optional[str] = None

    class Config:
        from_attributes = True


class ShareResponse(BaseModel):
    message: str
    share: Optional[ShareOut] = None
    shares_count: int


# ==============================
# VIEW SCHEMAS
# ==============================

class ViewCreate(BaseModel):
    news_uid: str = Field(..., description="News UID to view")


class ViewOut(BaseModel):
    id: int
    news_uid: str
    user_uid: Optional[str] = None
    viewed_at: datetime

    class Config:
        from_attributes = True


class ViewResponse(BaseModel):
    message: str
    view: Optional[ViewOut] = None
    views_count: int


# ==============================
# ENGAGEMENT STATS SCHEMAS
# ==============================

class EngagementStats(BaseModel):
    news_uid: str
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    user_reaction: Optional[int] = None
    user_has_shared: bool = False
