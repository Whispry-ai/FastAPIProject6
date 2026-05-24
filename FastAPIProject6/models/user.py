# from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Boolean
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from datetime import datetime, timedelta
# from database import Base
# from sqlalchemy import Table, Column, Integer, ForeignKey



# class OTPStore(Base):
#     __tablename__ = "otp_store"
#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String(10), nullable=False)
#     value = Column(String(100), nullable=False)
#     otp = Column(String(100), nullable=False)
#     verified = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5))

# # class User(Base):
# #     __tablename__ = "users"
# #     id = Column(Integer, primary_key=True, index=True)
# #     user_uid = Column(String(8), unique=True, index=True, nullable=False)
# #     phone = Column(String(15), unique=True, nullable=True)
# #     name = Column(String, nullable=True)
# #     gender = Column(String, nullable=True)
# #     role = Column(Integer, default=0)
# #     language = Column(String, nullable=True, index=True)
# #     state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
# #     district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
# #     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
# #     email = Column(String(25), unique=True, nullable=True)
# #     user_name = Column(String(10), unique=True, nullable=True)
# #     email_verified = Column(Boolean, default=False)
# #     mobile_verified = Column(Boolean, default=False)
# #     date_of_birth = Column(Date, nullable=True)
# #     created_at = Column(DateTime(timezone=True), server_default=func.now())
# #     token_version = Column(Integer, default=0)

# #     state = relationship("State")
# #     district = relationship("District")
# #     city = relationship("City")
# #     news = relationship("News", back_populates="user", foreign_keys="[News.user_uid]")
# #     approved_news = relationship("News", back_populates="approver", foreign_keys="[News.approved_by_uid]")
# #     preferences = relationship("UserPreference", back_populates="user")

# # models/user.py - Add these fields to your User class

# # class User(Base):
# #     __tablename__ = "users"
# #     id = Column(Integer, primary_key=True, index=True)
# #     user_uid = Column(String(8), unique=True, index=True, nullable=False)
# #     phone = Column(String(15), unique=True, nullable=True)
# #     name = Column(String, nullable=True)
# #     gender = Column(String, nullable=True)
# #     role = Column(Integer, default=0)
# #     language = Column(String, nullable=True, index=True)
# #     state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
# #     district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
# #     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
# #     email = Column(String(25), unique=True, nullable=True)
# #     user_name = Column(String(18), unique=True, nullable=True)  # ✅ Max 18 chars
# #     email_verified = Column(Boolean, default=False)
# #     mobile_verified = Column(Boolean, default=False)
# #     date_of_birth = Column(Date, nullable=True)
# #     created_at = Column(DateTime(timezone=True), server_default=func.now())
# #     token_version = Column(Integer, default=0)
    
# #     # ✅ ADD THESE NEW FIELDS FOR SUSPENSION
# #     is_suspended = Column(Boolean, default=False, index=True)
# #     suspension_reason = Column(String(500), nullable=True)
# #     suspended_at = Column(DateTime(timezone=True), nullable=True)
# #     suspended_until = Column(DateTime(timezone=True), nullable=True)
# #     suspended_by = Column(String(8), ForeignKey("users.user_uid"), nullable=True)  # Admin who suspended
# #     activated_at = Column(DateTime(timezone=True), nullable=True)  # When reactivated
# #     last_login = Column(DateTime(timezone=True), nullable=True)
# # models/user.py - Add the missing relationship

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     user_uid = Column(String(8), unique=True, index=True, nullable=False)
#     phone = Column(String(15), unique=True, nullable=True)
#     name = Column(String, nullable=True)
#     gender = Column(String, nullable=True)
#     role = Column(Integer, default=0)
#     language = Column(String, nullable=True, index=True)
#     state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
#     district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
#     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
#     email = Column(String(25), unique=True, nullable=True)
#     user_name = Column(String(18), unique=True, nullable=True)
#     email_verified = Column(Boolean, default=False)
#     mobile_verified = Column(Boolean, default=False)
#     date_of_birth = Column(Date, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     token_version = Column(Integer, default=0)
    
#     # Suspension fields
#     is_suspended = Column(Boolean, default=False, index=True)
#     suspension_reason = Column(String(500), nullable=True)
#     suspended_at = Column(DateTime(timezone=True), nullable=True)
#     suspended_until = Column(DateTime(timezone=True), nullable=True)
#     suspended_by = Column(String(8), ForeignKey("users.user_uid"), nullable=True)
#     activated_at = Column(DateTime(timezone=True), nullable=True)
#     last_login = Column(DateTime(timezone=True), nullable=True)

#     state = relationship("State")
#     district = relationship("District")
#     city = relationship("City")
    
#     # Existing relationships
#     news = relationship("News", back_populates="user", foreign_keys="[News.user_uid]")
#     approved_news = relationship("News", back_populates="approver", foreign_keys="[News.approved_by_uid]")
    
#     # ✅ ADD THIS - Rejected news relationship
#     rejected_news = relationship("News", back_populates="rejector", foreign_keys="[News.rejected_by_uid]")
    
#     preferences = relationship("UserPreference", back_populates="user")
#     suspended_by_user = relationship("User", foreign_keys=[suspended_by], remote_side=[user_uid])

# #     state = relationship("State")
# #     district = relationship("District")
# #     city = relationship("City")
# #     news = relationship("News", back_populates="user", foreign_keys="[News.user_uid]")
# #     approved_news = relationship("News", back_populates="approver", foreign_keys="[News.approved_by_uid]")
# #     preferences = relationship("UserPreference", back_populates="user")
    
# #     # ✅ ADD RELATIONSHIP FOR SUSPENDER
# #     suspended_by_user = relationship("User", foreign_keys=[suspended_by], remote_side=[user_uid])

# # class UserPreference(Base):
# #     __tablename__ = "user_preferences"
# #     id = Column(Integer, primary_key=True, index=True)
# #     user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
# #     language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
# #     state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
# #     district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
# #     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
# #     created_at = Column(DateTime, default=datetime.utcnow)
# #     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
# #     language = relationship("Language")
# #     state = relationship("State")
# #     district = relationship("District")
# #     city = relationship("City")
# #     user = relationship("User", back_populates="preferences")


# user_preference_categories = Table(
#     "user_preference_categories",
#     Base.metadata,
#     Column("preference_id", Integer, ForeignKey("user_preferences.id")),
#     Column("category_id", Integer, ForeignKey("categories.id"))
# )

# class UserPreference(Base):
#     __tablename__ = "user_preferences"

#     id = Column(Integer, primary_key=True, index=True)
#     user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
#     language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
#     state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
#     district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
#     city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     categories = relationship(
#         "Category",
#         secondary=user_preference_categories,
#         backref="user_preferences"
#     )

#     language = relationship("Language")
#     state = relationship("State")
#     district = relationship("District")
#     city = relationship("City")
#     user = relationship("User", back_populates="preferences")


# models/user.py

from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from database import Base
from sqlalchemy import Table, Column, Integer, ForeignKey


class OTPStore(Base):
    __tablename__ = "otp_store"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)
    value = Column(String(100), nullable=False)
    otp = Column(String(100), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5))


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(8), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=True)
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    role = Column(Integer, default=0)
    language = Column(String, nullable=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    email = Column(String(25), unique=True, nullable=True)
    user_name = Column(String(18), unique=True, nullable=True)
    email_verified = Column(Boolean, default=False)
    mobile_verified = Column(Boolean, default=False)
    date_of_birth = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_version = Column(Integer, default=0)
    
    # Suspension fields
    is_suspended = Column(Boolean, default=False, index=True)
    suspension_reason = Column(String(500), nullable=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    suspended_until = Column(DateTime(timezone=True), nullable=True)
    suspended_by = Column(String(8), ForeignKey("users.user_uid"), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Role switch tracking
    switched_by = Column(String(8), ForeignKey("users.user_uid"), nullable=True)
    switched_at = Column(DateTime(timezone=True), nullable=True)

    # ==============================
    # Relationships
    # ==============================
    
    # Location relationships
    state = relationship("State", foreign_keys=[state_id])
    district = relationship("District", foreign_keys=[district_id])
    city = relationship("City", foreign_keys=[city_id])
    
    # News relationships
    news = relationship(
        "News", 
        back_populates="user", 
        foreign_keys="[News.user_uid]"
    )
    
    approved_news = relationship(
        "News", 
        back_populates="approver", 
        foreign_keys="[News.approved_by_uid]"
    )
    
    rejected_news = relationship(
        "News", 
        back_populates="rejector", 
        foreign_keys="[News.rejected_by_uid]"
    )
    
    # User preferences
    preferences = relationship("UserPreference", back_populates="user")
    
    # Self-referential relationships
    suspended_by_user = relationship(
        "User", 
        foreign_keys=[suspended_by], 
        remote_side=[user_uid]
    )
    
    switched_by_user = relationship(
        "User", 
        foreign_keys=[switched_by], 
        remote_side=[user_uid]
    )
    
    # Backward compatibility property
    @property
    def uid(self):
        """Backward compatibility property for uid"""
        return self.user_uid


# Association table for user preferences categories
user_preference_categories = Table(
    "user_preference_categories",
    Base.metadata,
    Column("preference_id", Integer, ForeignKey("user_preferences.id")),
    Column("category_id", Integer, ForeignKey("categories.id"))
)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String, ForeignKey("users.user_uid"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = relationship(
        "Category",
        secondary=user_preference_categories,
        backref="user_preferences"
    )

    language = relationship("Language")
    state = relationship("State")
    district = relationship("District")
    city = relationship("City")
    user = relationship("User", back_populates="preferences")