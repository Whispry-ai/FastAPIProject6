from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class GuestUser(Base):
    __tablename__ = "guest_users"
    id = Column(Integer, primary_key=True, index=True)
    guest_uid = Column(String(10), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    device_id = Column(String(100), nullable=True)
    device_name = Column(String(100), nullable=True)
    android_version = Column(String(20), nullable=True)
    app_version = Column(String(20), nullable=True)
    app_version_code = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    state = relationship("State")
    district = relationship("District")
    city = relationship("City")

class GuestPreference(Base):
    __tablename__ = "guest_preferences"
    id = Column(Integer, primary_key=True, index=True)
    guest_uid = Column(String, ForeignKey("guest_users.guest_uid", ondelete="CASCADE"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    language = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    __table_args__ = (
        UniqueConstraint("guest_uid", "city_id", "language", name="uq_guest_location"),
        Index("ix_guest_preferences_guest_uid", "guest_uid"),
        Index("ix_guest_preferences_language", "language"),
        Index("ix_guest_preferences_city_id", "city_id"),
    )
    guest = relationship("GuestUser", backref="preferences", passive_deletes=True)
    state = relationship("State")
    district = relationship("District")
    city = relationship("City")
