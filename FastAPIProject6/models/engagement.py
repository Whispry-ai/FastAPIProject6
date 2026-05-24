from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
    content_type = Column(String, nullable=False)
    content_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("user_uid", "content_type", "content_id", name="unique_bookmark"),)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link_url = Column(String, nullable=True)
    notification_type = Column(String, default="custom")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")
