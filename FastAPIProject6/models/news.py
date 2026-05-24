# from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table, UniqueConstraint
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from database import Base

# news_categories = Table(
#     "news_categories",
#     Base.metadata,
#     Column("news_id", Integer, ForeignKey("news.id")),
#     Column("category_id", Integer, ForeignKey("categories.id")),
# )

# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, nullable=False)
#     news = relationship("News", secondary=news_categories, back_populates="categories")

# class News(Base):
#     __tablename__ = "news"
#     id = Column(Integer, primary_key=True, index=True)
#     news_uid = Column(String(6), unique=True, index=True, nullable=False)
#     title = Column(String, nullable=False)
#     summary = Column(String, nullable=False)
#     image_url = Column(String, nullable=True)
#     language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
#     is_approved = Column(Integer, default=0, index=True)
#     is_auto_generated = Column(Boolean, default=False)
#     source_url = Column(String, nullable=True)
#     source_name = Column(String, nullable=True)
#     rejected_at = Column(DateTime, nullable=True)
#     user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
#     approved_by_uid = Column(String, ForeignKey("users.user_uid"), nullable=True)
#     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     user = relationship("User", back_populates="news", foreign_keys=[user_uid])
#     approver = relationship("User", back_populates="approved_news", foreign_keys=[approved_by_uid])
#     city = relationship("City", back_populates="news")
#     language = relationship("Language", back_populates="news")
#     categories = relationship("Category", secondary=news_categories, back_populates="news")
#     reactions = relationship("Reaction", backref="news", cascade="all, delete", passive_deletes=True)
#     comments = relationship("Comment", backref="news", cascade="all, delete", passive_deletes=True)

# class Reaction(Base):
#     __tablename__ = "reactions"
#     id = Column(Integer, primary_key=True, index=True)
#     user_uid = Column(String, nullable=False)
#     news_uid = Column(String(6), ForeignKey("news.news_uid", ondelete="CASCADE"), nullable=False)
#     reaction_type = Column(Integer, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

# class Comment(Base):
#     __tablename__ = "comments"
#     id = Column(Integer, primary_key=True, index=True)
#     user_uid = Column(String, nullable=False)
#     news_uid = Column(String(6), ForeignKey("news.news_uid", ondelete="CASCADE"), nullable=False)
#     comment_text = Column(Text, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

# class Share(Base):
#     __tablename__ = "shares"
#     id = Column(Integer, primary_key=True, index=True)
#     news_uid = Column(String(6), ForeignKey("news.news_uid", ondelete="CASCADE"), nullable=False)
#     user_uid = Column(String, nullable=False)
#     shared_at = Column(DateTime(timezone=True), server_default=func.now())
#     platform = Column(String, nullable=True)
#     __table_args__ = (UniqueConstraint("news_uid", "user_uid", name="unique_user_news_share"),)
    
# class NewsView(Base):
#     __tablename__ = "news_views"

#     id = Column(Integer, primary_key=True, index=True)
#     news_uid = Column(String(6), ForeignKey("news.news_uid", ondelete="CASCADE"), nullable=False)
#     user_uid = Column(String, nullable=True)
#     viewed_at = Column(DateTime(timezone=True), server_default=func.now())


from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey,
    Text, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# ==============================
# Association Table
# ==============================

news_categories = Table(
    "news_categories",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)


# ==============================
# Category Model
# ==============================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    news = relationship(
        "News",
        secondary=news_categories,
        back_populates="categories"
    )


# ==============================
# News Model
# ==============================

# models/news.py - Add missing fields to News class

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)

    news_uid = Column(String(6), unique=True, nullable=False, index=True)

    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    image_url = Column(String, nullable=True)

    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)

    is_approved = Column(Integer, default=0, index=True)
    is_auto_generated = Column(Boolean, default=False)

    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)

    # Missing fields
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
    approved_by_uid = Column(String, ForeignKey("users.user_uid"), nullable=True)
    rejected_by_uid = Column(String, ForeignKey("users.user_uid"), nullable=True)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_breaking = Column(Boolean, default=False, index=True)

    breaking_priority = Column(Integer, default=0)
    breaking_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Engagement Counters
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)

    # ==============================
    # Relationships
    # ==============================

    user = relationship(
        "User",
        back_populates="news",
        foreign_keys=[user_uid]
    )

    approver = relationship(
        "User",
        back_populates="approved_news",
        foreign_keys=[approved_by_uid]
    )

    # ✅ FIXED: No backref here since User model has rejected_news
    rejector = relationship(
        "User",
        foreign_keys=[rejected_by_uid],
        back_populates="rejected_news"  # ✅ This matches User model's relationship
    )

    city = relationship("City", back_populates="news")
    language = relationship("Language", back_populates="news")

    categories = relationship(
        "Category",
        secondary=news_categories,
        back_populates="news"
    )

    reactions = relationship(
        "Reaction",
        backref="news",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    comments = relationship(
        "Comment",
        backref="news",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    shares = relationship(
        "Share",
        backref="news",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    views = relationship(
        "NewsView",
        backref="news",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
# ==============================
# Reaction Model
# ==============================

class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)

    user_uid = Column(String, nullable=False, index=True)

    news_uid = Column(
        String(6),
        ForeignKey("news.news_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    reaction_type = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_uid",
            "news_uid",
            "reaction_type",
            name="unique_user_news_reaction"
        ),
    )


# ==============================
# Comment Model
# ==============================

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    user_uid = Column(String, nullable=False, index=True)

    news_uid = Column(
        String(6),
        ForeignKey("news.news_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    comment_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==============================
# Share Model
# ==============================

class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)

    news_uid = Column(
        String(6),
        ForeignKey("news.news_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_uid = Column(String, nullable=False, index=True)

    shared_at = Column(DateTime(timezone=True), server_default=func.now())

    platform = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "news_uid",
            "user_uid",
            name="unique_user_news_share"
        ),
    )


# ==============================
# News Views Model
# ==============================

class NewsView(Base):
    __tablename__ = "news_views"

    id = Column(Integer, primary_key=True, index=True)

    news_uid = Column(
        String(6),
        ForeignKey("news.news_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_uid = Column(String, nullable=True, index=True)

    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
# models/news.py - Add this class

# Add this at the end of your models/news.py (after all existing models)

# ==============================
# News Flag Model (for moderation)
# ==============================

class NewsFlag(Base):
    __tablename__ = "news_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    news_uid = Column(
        String(6),
        ForeignKey("news.news_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_uid = Column(
        String,
        ForeignKey("users.user_uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending", index=True)  # pending, reviewed, dismissed
    review_notes = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    news = relationship("News", backref="flags")
    user = relationship("User", backref="flags")
    
    __table_args__ = (
        UniqueConstraint("news_uid", "user_uid", name="unique_user_news_flag"),
    )
    
# Add this at the end of your models/news.py (after NewsFlag)

# ==============================
# Scheduled News Model
# ==============================

class ScheduledNews(Base):
    __tablename__ = "scheduled_news"

    id = Column(Integer, primary_key=True, index=True)
    
    news_uid = Column(String(6), unique=True, nullable=False, index=True)
    
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    
    user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
    scheduled_by = Column(String, ForeignKey("users.user_uid"), nullable=False)
    
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, index=True)
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)
    
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(20), default="pending", index=True)  # pending, published, failed, cancelled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_uid])
    scheduler = relationship("User", foreign_keys=[scheduled_by])
    language = relationship("Language")
    city = relationship("City")
    categories = relationship(
        "Category",
        secondary="scheduled_news_categories",
        backref="scheduled_news"
    )


# ==============================
# Scheduled News Categories Association Table
# ==============================

scheduled_news_categories = Table(
    "scheduled_news_categories",
    Base.metadata,
    Column("scheduled_news_id", Integer, ForeignKey("scheduled_news.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)