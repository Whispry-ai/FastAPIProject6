"""
Schemas for the application using Pydantic models.
Organized by category for better readability.
Standardized to Pydantic v2 conventions (e.g., model_config with from_attributes=True).
Removed duplicates, unused imports, and inconsistencies.
"""

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl, EmailStr, Field, ConfigDict
from typing import Any, Optional, List, Literal, Union, Dict
from datetime import datetime
from enum import IntEnum

# =============================================================================
# Enums
# =============================================================================

class UserRole(IntEnum):
    """User  roles for access control."""
    GUEST = 0
    USER = 1
    PUBLISHER = 4 # Reporter
    EMPLOYEE = 3
    ADMIN = 5


# =============================================================================
# Authentication & OTP Schemas
# =============================================================================

class TokenResponse(BaseModel):
    """Response containing authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int
    email: Optional[str] = None


class RoleAssignRequest(BaseModel):
    """Request to assign a new role to a user."""
    user_id: str
    new_role: Literal[0, 1, 2, 3, 4]  # GUEST to ADMIN


class AdminLoginRequest(BaseModel):
    """Request for admin login with OTP support."""
    identifier: str  # email or phone
    role: int  # expected role
    otp: Optional[str] = None


class SendOtpRequest(BaseModel):
    """Request to send OTP via email or mobile."""
    type: str  # 'mobile' or 'email' (constrained externally if needed)
    value: str  # phone number or email


class VerifyOtp(BaseModel):
    """Request to verify OTP."""
    type: Literal["email", "mobile"]
    value: str
    otp: str


class OTPVerifyRequest(BaseModel):
    """Request to verify OTP for user registration/login."""
    user_uid: str
    email: Optional[EmailStr] = None
    email_otp: Optional[str] = None
    mobile: Optional[str] = None
    mobile_otp: Optional[str] = None


class SendOtp(BaseModel):
    """Simple request to send OTP (alternative/duplicate consolidated)."""
    type: str  # "mobile" or "email"
    value: str  # phone number or email


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    """Base user model with common fields."""
    phone: str
    name: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    email_verified: Optional[bool] = False
    mobile_verified: Optional[bool] = False


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserOut(UserBase):
    """Output schema for user details."""
    user_uid: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsUserInfo(BaseModel):
    """User  info for news-related contexts."""
    user_uid: str
    name: Optional[str] = None
    phone: Optional[str] = None


# =============================================================================
# Location Schemas (State, District, City, Language)
# =============================================================================

class LanguageCreate(BaseModel):
    """Schema for creating a language."""
    code: str
    name: str


class LanguageResponse(BaseModel):
    """Response schema for language details."""
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class LanguageOut(LanguageResponse):
    """Output schema for language (alias/consolidated)."""
    pass


class StateCreate(BaseModel):
    """Schema for creating a state."""
    name: str


class StateResponse(BaseModel):
    """Response schema for state details."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StateOut(StateResponse):
    """Output schema for state (alias/consolidated)."""
    pass


class DistrictCreate(BaseModel):
    """Schema for creating a district."""
    name: str
    state_id: int


class DistrictOut(BaseModel):
    """Output schema for district details."""
    id: int
    name: str
    state_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CityCreate(BaseModel):
    """Schema for creating a city."""
    name: str
    district_id: int


class CityOut(BaseModel):
    """Output schema for city details."""
    id: int
    name: str
    district_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CityRef(BaseModel):
    """Reference schema for city (lightweight)."""
    id: int
    name: str


class StateLanguageResponse(BaseModel):
    """Combined response for state and language."""
    state: StateResponse
    language: Optional[LanguageResponse] = None
    message: Optional[str] = None


# =============================================================================
# Category Schemas
# =============================================================================

class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str


class CategoryOut(BaseModel):
    """Output schema for category details."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# News Schemas
# =============================================================================

# class NewsCreate(BaseModel):
#     """Schema for creating news."""
#     title: str
#     summary: str
#     image_url: Optional[str] = None
#     language_id: int
#     user_uid: str
#     city_id: Optional[int] = None
#     category_ids: Optional[List[int]] = []
#     source_url: Optional[str] = None
#     source_name: Optional[str] = None
class EngagementOut(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    user_liked: bool = False
    

    
class NewsCreate(BaseModel):
    title: str
    summary: str
    image_url: Optional[HttpUrl] = None
    language_id: int
    user_uid: str
    city_id: Optional[int] = None
    category_ids: List[int] = Field(default_factory=list)
    source_url: Optional[HttpUrl] = None
    source_name: Optional[str] = None

class NewsUpdate(BaseModel):
    """Schema for updating news."""
    title: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    language_id: Optional[int] = None
    city_id: Optional[int] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    category_ids: Optional[List[int]] = None



class NewsOut(BaseModel):
    """Detailed output schema for news."""

    news_uid: str
    title: str
    summary: str
    image_url: Optional[str] = None

    language: Optional[LanguageOut] = None

    user_uid: str
    is_approved: int
    created_at: Optional[datetime] = None

    city: Optional[CityOut] = None
    district: Optional[DistrictOut] = None
    state: Optional[StateOut] = None

    source_url: Optional[str] = None
    source_name: Optional[str] = None

    category_ids: List[int] = []

    engagement: Optional[EngagementOut] = None

    model_config = ConfigDict(from_attributes=True)
#before updated the engagements section
# class NewsOut(BaseModel):
#     """Detailed output schema for news."""
#     news_uid: str
#     title: str
#     summary: str
#     image_url: Optional[str] = None
#     language: Optional[LanguageOut] = None
#     user_uid: str
#     is_approved: int
#     created_at: Optional[datetime] = None
#     city: Optional[CityOut] = None
#     district: Optional[DistrictOut] = None
#     state: Optional[StateOut] = None
#     source_url: Optional[str] = None
#     source_name: Optional[str] = None
#     category_ids: List[int] = []

#     model_config = ConfigDict(from_attributes=True)


class PublicNewsOut(BaseModel):
    """Public-facing output schema for approved news."""
    news_uid: str
    title: str
    summary: str
    image_url: Optional[str] = None
    language: Optional[str] = None
    is_approved: int
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    created_at: datetime
    category_names: List[str]
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# class AdminNewsDetailsOut(BaseModel):
#     """Admin view of news with approver info."""
#     news_uid: str
#     title: str
#     summary: str
#     image_url: Optional[str] = None
#     language: Optional[LanguageOut] = None
#     is_approved: int
#     source_url: Optional[str] = None
#     source_name: Optional[str] = None
#     created_at: Optional[datetime] = None
#     category_names: List[str] = []
#     state: Optional[str] = None
#     district: Optional[str] = None
#     city: Optional[str] = None
#     user_name: Optional[str] = None
#     posted_by: Optional[Dict] = None
#     approved_by: Optional[Dict] = None

class AdminEngagementOut(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0


class AdminNewsDetailsOut(BaseModel):
    news_uid: str
    title: str
    summary: str
    image_url: Optional[str]

    language: Optional[dict]

    is_approved: int
    source_url: Optional[str]
    source_name: Optional[str]

    created_at: Optional[datetime]

    category_names: List[str]

    state: Optional[str]
    district: Optional[str]
    city: Optional[str]

    user_name: Optional[str]

    posted_by: Optional[dict]
    approved_by: Optional[dict]

    engagement: AdminEngagementOut

class AdminNewsItemOut(BaseModel):
    """Admin list item for news."""
    news_uid: str
    title: str
    summary: str
    image_url: Optional[str] = None
    language: Optional[str] = None
    is_approved: int
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    created_at: Optional[datetime] = None
    category_names: List[str]
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    user_name: Optional[str] = None
    user_uid: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsURLInput(BaseModel):
    """Input for news from URL."""
    url: HttpUrl
    user_uid: str
    state: Optional[str] = None


class AutoNewsCreate(BaseModel):
    """Schema for auto-generated news from sources."""
    source_url: str
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    state_id: Optional[int] = None
    category_ids: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Sponsored Posts & Advertisements
# =============================================================================

# class SponsoredPostCreate(BaseModel):
#     """Schema for creating a sponsored post."""
#     title: str
#     content: str
#     image_url: str
#     cta_text: str
#     cta_url: str
#     state: Optional[str] = None
#     district: Optional[str] = None
#     city: Optional[str] = None
#     start_date: datetime
#     end_date: datetime


# class SponsoredPostOut(SponsoredPostCreate):
#     """Output schema for sponsored post."""
#     id: int
#     is_approved: bool
#     created_at: datetime

#     model_config = ConfigDict(from_attributes=True)


# class SponsoredItem(BaseModel):
#     """Lightweight sponsored item for feeds."""
#     id: int
#     title: str
#     content: str
#     image_url: Optional[str] = None
#     cta_text: Optional[str] = None
#     cta_url: Optional[str] = None
#     start_date: datetime
#     end_date: datetime

#     model_config = ConfigDict(from_attributes=True)


# class AdvertisementBase(BaseModel):
#     """Base schema for advertisements."""
#     title: str
#     image_url: str
#     redirect_url: Optional[str] = None
#     placement: str
#     start_date: datetime
#     end_date: datetime
#     state_id: Optional[int] = None
#     district_id: Optional[int] = None
#     city_id: Optional[int] = None
#     is_active: bool = True


# class AdvertisementCreate(AdvertisementBase):
#     """Schema for creating an advertisement."""
#     pass


# class AdvertisementOut(AdvertisementBase):
#     """Output schema for advertisement."""
#     id: int

#     model_config = ConfigDict(from_attributes=True)


# class AdItem(BaseModel):
#     """Lightweight ad item for feeds."""
#     id: int
#     title: str
#     image_url: str
#     redirect_url: Optional[str] = None
#     placement: str
#     start_date: datetime
#     end_date: datetime
#     is_active: bool = True

#     model_config = ConfigDict(from_attributes=True)

# =============================================================================
# Enhanced Ad Schemas
# =============================================================================

class AdTargeting(BaseModel):
    """Targeting options for ads and sponsored posts"""
    languages: Optional[List[int]] = Field(None, description="Language IDs")
    states: Optional[List[int]] = Field(None, description="State IDs")
    districts: Optional[List[int]] = Field(None, description="District IDs")
    cities: Optional[List[int]] = Field(None, description="City IDs")
    gender: Optional[str] = Field(None, pattern="^(male|female|all)$", description="Target gender")
    age_min: Optional[int] = Field(None, ge=13, le=100, description="Minimum age")
    age_max: Optional[int] = Field(None, ge=13, le=100, description="Maximum age")


class AdvertisementCreate(BaseModel):
    """Schema for creating an advertisement"""
    title: str = Field(..., max_length=200)
    image_url: str = Field(..., max_length=500)
    redirect_url: Optional[str] = Field(None, max_length=500)
    placement: str = Field(..., description="banner, interstitial, native, feed")
    start_date: datetime
    end_date: datetime
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    language_id: Optional[int] = None
    is_active: bool = True
    targeting: Optional[AdTargeting] = None


class AdvertisementOut(BaseModel):
    """Output schema for advertisement"""
    id: int
    title: str
    image_url: str
    redirect_url: Optional[str]
    placement: str
    start_date: datetime
    end_date: datetime
    state_id: Optional[int]
    district_id: Optional[int]
    city_id: Optional[int]
    language_id: Optional[int]
    target_gender: Optional[str]
    target_age_min: Optional[int]
    target_age_max: Optional[int]
    is_active: bool
    is_premium: bool = False  # ✅ ADD THIS
    premium_priority: int = 0  # ✅ ADD THIS
    created_at: datetime
    updated_at: Optional[datetime]
    relevance_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# In schemas.py
class SponsoredPostCreate(BaseModel):
    """Schema for creating a sponsored post."""
    title: str
    content: str
    image_url: str
    cta_text: str
    cta_url: str
    state_id: Optional[int] = None      # ← Change to state_id
    district_id: Optional[int] = None   # ← Change to district_id
    city_id: Optional[int] = None       # ← Change to city_id
    language_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    targeting: Optional[AdTargeting] = None


class SponsoredPostOut(BaseModel):
    """Output schema for sponsored post."""
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    start_date: datetime
    end_date: datetime
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    language_id: Optional[int] = None
    target_gender: Optional[str] = None
    target_age_min: Optional[int] = None
    target_age_max: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_approved: bool = False
    
    class Config:
        from_attributes = True
    
    
# Add to schemas.py

# Add these paginated schemas to your schemas.py

class PaginatedAdvertisementsOut(BaseModel):
    """Paginated response for advertisements"""
    total: int
    page: int
    limit: int
    items: List[AdvertisementOut]
    
    class Config:
        from_attributes = True


class PaginatedSponsoredPostsOut(BaseModel):
    """Paginated response for sponsored posts"""
    total: int
    page: int
    limit: int
    items: List[SponsoredPostOut]
    
    class Config:
        from_attributes = True
# =============================================================================
# Events
# =============================================================================

class EventCreate(BaseModel):
    """Schema for creating an event."""
    title: str
    description: str
    image_url: Optional[str] = None
    event_date: datetime
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: str
    is_online: bool = False
    event_url: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


class EventOut(EventCreate):
    """Output schema for event."""
    id: int
    event_uid: str
    is_approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Polls
# =============================================================================

class PollCreate(BaseModel):
    """Schema for creating a poll."""
    question: str
    options: List[str]
    expires_at: Optional[datetime] = None


class PollVote(BaseModel):
    """Schema for voting in a poll."""
    poll_uid: str
    option_index: int
    user_uid: str


class PollOut(BaseModel):
    """Basic output schema for poll."""
    poll_uid: str
    question: str
    options: List[str]
    votes: List[int]
    expires_at: Optional[datetime] = None


class PollDetailOut(BaseModel):
    """Detailed output schema for poll."""
    poll_uid: str
    question: str
    options: List[str]
    votes: List[int]
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Bookmarks
# =============================================================================

class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark."""
    user_uid: str
    content_type: Literal["news", "event", "poll"]
    content_id: int


class BookmarkOut(BookmarkCreate):
    """Output schema for bookmark."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Feed & Shared Items
# =============================================================================

class NewsItem(BaseModel):
    """News item for feeds."""
    id: int
    news_uid: str
    title: str
    summary: str
    image_url: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime
    reaction_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsFeedItem(BaseModel):
    """News item for news feed."""
    news_uid: str
    title: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    language: str
    is_approved: int
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    created_at: datetime
    category_names: List[str]
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FeedItem(BaseModel):
    """Generic feed item supporting multiple types."""
    type: Literal["news", "sponsored", "ad"]
    data: Union[NewsItem, SponsoredPostOut, AdvertisementOut]


class ApproverInfo(BaseModel):
    """Info for approvers in admin contexts."""
    user_uid: str
    name: Optional[str] = None
    phone: Optional[str] = None


# =============================================================================
# Video & Shorts
# =============================================================================

class VideoItem(BaseModel):
    """Schema for video items (e.g., YouTube)."""
    title: str
    video_id: str
    thumbnail_url: str
    channel_title: str
    published_at: str


class NewsShortCreate(BaseModel):
    """Schema for creating news shorts from videos."""
    videoId: str
    title: str
    thumbnail: str
    channel: str
    publishedAt: datetime
    videoUrl: str


# =============================================================================
# Notifications & Admin
# =============================================================================

class BreakingNewsUpdate(BaseModel):
    is_breaking: bool
    priority: int = 5
    expire_hours: int = 6

class AdminNotificationRequest(BaseModel):
    """Request for sending admin notifications."""
    title: str
    message: str
    link_url: Optional[str] = None
    target_type: Literal["all", "state", "district", "city", "user"]
    target_value: Optional[str] = None  # UID or name based on target_type


class NotificationOut(BaseModel):
    """Output schema for notifications."""
    id: int
    user_uid: str
    title: str
    message: str
    link_url: Optional[str] = None
    notification_type: Optional[str] = None
    created_at: datetime
    is_read: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel
from typing import List

class DashboardStat(BaseModel):
    total: int
    today: int | None = None


class EngagementStats(BaseModel):
    views: int
    likes: int
    comments: int
    shares: int


class TopReporter(BaseModel):
    user_uid: str
    name: str
    news_count: int


class TrendingNews(BaseModel):
    news_uid: str
    title: str
    views: int


class AdminDashboardOut(BaseModel):

    news: DashboardStat
    users: DashboardStat
    ads: DashboardStat
    events: DashboardStat
    polls: DashboardStat

    engagement: EngagementStats

    pending_news: int
    rejected_news: int

    top_reporters: List[TopReporter]

    trending_news: List[TrendingNews]
    
    
class DailyMetric(BaseModel):
    date: str
    news_posted: int
    views: int
    likes: int
    comments: int
    shares: int


class UserGrowth(BaseModel):
    date: str
    new_users: int


class AdminNewsAnalyticsOut(BaseModel):
    daily_metrics: List[DailyMetric]
    user_growth: List[UserGrowth]
# =============================================================================
# User/Guest Preferences
# =============================================================================

class UserPreferenceCreate(BaseModel):
    user_uid: str
    language_id: int
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    category_ids: List[int] = Field(default_factory=list)


    model_config = ConfigDict(from_attributes=True)


# class UserPreferenceResponse(BaseModel):
#     """Response schema for user preferences."""
#     user_uid: str
#     language: str  # language code like "te", "hi", "en"
#     state_id: Optional[int] = None
#     district_id: Optional[int] = None
#     city_id: Optional[int] = None
#     created_at: datetime
#     updated_at: datetime
class UserPreferenceResponse(BaseModel):
    user_uid: str
    language: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    category_ids: List[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GuestCreateRequest(BaseModel):
    """Schema for creating a guest session."""
    device_id: str
    device_name: str
    android_version: str
    app_version: str
    app_version_code: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


class GuestResponse(BaseModel):
    """Response schema for guest details."""
    guest_uid: str
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    android_version: Optional[str] = None
    app_version: Optional[str] = None
    app_version_code: Optional[str] = None
    created_at: Optional[datetime] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class GuestPreferenceCreate(BaseModel):
    """Schema for creating guest preferences."""
    guest_uid: str
    language: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


class GuestPreferenceUpdate(BaseModel):
    """Schema for updating guest preferences."""
    language: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


# Add these new schemas to your existing schemas.py



# =============================
# Content Scheduling Schemas
# =============================

class ScheduledContentBase(BaseModel):
    content_type: str = Field(..., description="Type: sponsored_post, advertisement, event, poll")
    content_id: int = Field(..., description="ID of the content")
    scheduled_at: datetime = Field(..., description="When to publish")

class ScheduledContentCreate(ScheduledContentBase):
    pass

class ScheduledContentOut(ScheduledContentBase):
    id: int
    status: str  # pending, published, failed
    published_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# =============================
# Flagged Content Schemas
# =============================

class FlaggedContentBase(BaseModel):
    content_type: str = Field(..., description="Type: news, event, poll, sponsored, advertisement")
    content_id: int
    reason: str = Field(..., max_length=500)

class FlaggedContentCreate(FlaggedContentBase):
    flagged_by: str

class FlaggedContentOut(FlaggedContentBase):
    id: int
    flagged_by: str
    status: str  # pending, reviewed, dismissed
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FlaggedContentReview(BaseModel):
    action: str = Field(..., description="approve, reject, or dismiss")
    review_notes: Optional[str] = None

# =============================
# Content Tags Schemas
# =============================

class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ContentTagsUpdate(BaseModel):
    tags: List[str] = Field(..., description="List of tag names to assign")

class TaggedContentOut(BaseModel):
    id: int
    content_type: str
    content_id: int
    tag: TagOut

# =============================
# Content Versioning Schemas
# =============================

class ContentVersionOut(BaseModel):
    id: int
    version_number: int
    data: Any
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True

# =============================
# Content Analytics Schemas
# =============================

class ContentAnalyticsOut(BaseModel):
    content_type: str
    content_id: int
    views: int
    clicks: int
    engagement_rate: float
    total_interactions: int
    period_start: datetime
    period_end: datetime
    daily_breakdown: List[dict]

class TopPerformingContentOut(BaseModel):
    content_type: str
    content_id: int
    title: str
    metric_value: int
    metric_type: str
    created_at: datetime

class ContentAnalyticsOverviewOut(BaseModel):
    total_content: int
    published_today: int
    published_this_week: int
    published_this_month: int
    top_performing: List[TopPerformingContentOut]
    engagement_trends: dict

# =============================
# Content Expiry Schemas
# =============================

class ContentExpiryUpdate(BaseModel):
    expires_at: datetime = Field(..., description="When content should expire")

class ExpiringContentOut(BaseModel):
    content_type: str
    content_id: int
    title: str
    expires_at: datetime
    days_until_expiry: int

# =============================
# Content Preview Schemas
# =============================

class ContentPreviewOut(BaseModel):
    content_type: str
    content_id: int
    data: dict
    preview_html: Optional[str] = None

# =============================
# Content Report Schemas
# =============================

class DailyReportOut(BaseModel):
    date: datetime
    content_created: dict  # Breakdown by type
    content_published: dict
    total_views: int
    total_engagement: int
    top_content: List[dict]

class MonthlyReportOut(BaseModel):
    year: int
    month: int
    summary: dict
    daily_breakdown: List[DailyReportOut]

# =============================
# Content Relationship Schemas
# =============================

class RelatedContentOut(BaseModel):
    content_type: str
    content_id: int
    title: str
    relationship_type: str
    created_at: datetime

class RelatedContentCreate(BaseModel):
    related_content_type: str
    related_content_id: int
    relationship_type: str = Field(default="related")

# =============================
# Content Template Schemas
# =============================

class ContentTemplateBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    content_type: str = Field(..., description="sponsored_post, advertisement, event, poll")
    template_data: dict
    description: Optional[str] = None

class ContentTemplateCreate(ContentTemplateBase):
    pass

class ContentTemplateOut(ContentTemplateBase):
    id: int
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True

# =============================
# Review Queue Schemas
# =============================

class ReviewQueueOut(BaseModel):
    id: int
    content_type: str
    content_id: int
    title: str
    submitted_by: str
    submitted_at: datetime
    priority: str = "medium"
    assigned_to: Optional[str] = None

# =============================
# Bulk Operation Schemas
# =============================

class BulkOperation(BaseModel):
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., description="approve, reject, delete, archive")

class BulkOperationResponse(BaseModel):
    total: int
    successful: int
    failed: int
    errors: List[dict] = []

# =============================
# Content Search Schemas
# =============================

class ContentSearchResults(BaseModel):
    total: int
    items: List[dict]
    page: int
    limit: int
    has_next: bool
    has_previous: bool
    
    
# Add these to your schemas.py



# ==============================
# News Analytics Schemas
# ==============================

class DailyNewsStats(BaseModel):
    date: str
    summary: dict
    top_news: List[dict]

class WeeklyNewsStats(BaseModel):
    week_start: str
    week_end: str
    summary: dict
    daily_breakdown: List[dict]
    top_categories: List[dict]

class MonthlyNewsStats(BaseModel):
    year: int
    month: int
    month_name: str
    summary: dict
    weekly_breakdown: List[dict]
    language_breakdown: List[dict]

class TopPerformingNews(BaseModel):
    rank: int
    news_uid: str
    title: str
    summary: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float

class TrendingNews(BaseModel):
    news_uid: str
    title: str
    image_url: Optional[str]
    views: int
    likes: int
    created_at: datetime
    age_hours: float
    views_per_hour: float
    trending_score: float

# ==============================
# News Moderation Schemas
# ==============================

class NewsFlagCreate(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)

class NewsFlagOut(BaseModel):
    id: int
    news_uid: str
    user_uid: str
    reason: str
    status: str
    review_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class FlagReview(BaseModel):
    action: str = Field(..., description="approve, reject, or dismiss")
    review_notes: Optional[str] = Field(None, max_length=500)

class PendingFlagOut(BaseModel):
    id: int
    type: str
    content_id: str
    content_title: str
    reporter_uid: str
    reporter_name: Optional[str]
    reason: str
    status: str
    created_at: datetime
    review_notes: Optional[str] = None
    
# Add to your schemas.py

# ==============================
# News Scheduling Schemas
# ==============================

class ScheduledNewsBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    summary: str = Field(..., min_length=10, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=500)
    language_id: int
    user_uid: str
    city_id: Optional[int] = None
    source_url: Optional[str] = Field(None, max_length=500)
    source_name: Optional[str] = Field(None, max_length=200)
    category_ids: List[int] = Field(default_factory=list)

class ScheduledNewsCreate(ScheduledNewsBase):
    scheduled_at: datetime = Field(..., description="When to publish the news")

class ScheduledNewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    summary: Optional[str] = Field(None, min_length=10, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=500)
    language_id: Optional[int] = None
    city_id: Optional[int] = None
    source_url: Optional[str] = Field(None, max_length=500)
    source_name: Optional[str] = Field(None, max_length=200)
    category_ids: Optional[List[int]] = None
    scheduled_at: Optional[datetime] = None

class ScheduledNewsOut(BaseModel):
    id: int
    news_uid: str
    title: str
    summary: str
    image_url: Optional[str] = None
    language_id: int
    user_uid: str
    city_id: Optional[int] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    category_ids: List[int] = []
    scheduled_at: datetime
    status: str
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
#==================================================================================================


#==================================================================
# Add to schemas.py

# =====================================================
# User Suspension Schemas
# =====================================================

class UserSuspendRequest(BaseModel):
    """Request to suspend a user"""
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for suspension")
    duration_days: int = Field(30, ge=1, le=365, description="Suspension duration in days")
    notify_user: bool = Field(True, description="Send notification to user")


class UserActivateRequest(BaseModel):
    """Request to activate a user"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for activation")


class UserSuspendResponse(BaseModel):
    """Response after suspending a user"""
    user_uid: str
    user_name: Optional[str]
    is_suspended: bool
    suspension_reason: str
    suspended_until: datetime
    suspended_by: str
    message: str


class UserSuspensionStatus(BaseModel):
    """Check suspension status of a user"""
    is_suspended: bool
    suspension_reason: Optional[str] = None
    suspended_at: Optional[datetime] = None
    suspended_until: Optional[datetime] = None
    suspended_by: Optional[str] = None
    days_remaining: Optional[int] = None


class UserSuspensionHistory(BaseModel):
    """Suspension history entry"""
    id: int
    user_uid: str
    reason: str
    suspended_at: datetime
    suspended_until: Optional[datetime] = None
    suspended_by: str
    activated_at: Optional[datetime] = None
    activated_by: Optional[str] = None
    was_permanent: bool = False
# =====================================================
# Admin User Creation Schemas
# =====================================================

class AdminUserPreferenceCreate(BaseModel):
    """Preferences for admin user creation"""
    language_id: int
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    category_ids: List[int] = Field(default_factory=list)


class AdminUserCreate(BaseModel):
    """Schema for admin creating a user"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    name: Optional[str] = Field(None, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$", description="Gender")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    language: Optional[str] = Field(None, description="Preferred language")
    state_id: Optional[int] = Field(None, description="State ID")
    district_id: Optional[int] = Field(None, description="District ID")
    city_id: Optional[int] = Field(None, description="City ID")
    role: int = Field(1, description="0:GUEST, 1:USER, 2:PUBLISHER, 3:EMPLOYEE, 4:ADMIN")
    email_verified: Optional[bool] = Field(None, description="Email verification status")
    mobile_verified: Optional[bool] = Field(None, description="Mobile verification status")
    preferences: Optional[AdminUserPreferenceCreate] = Field(None, description="User preferences")
    

# Add these after your existing User schemas (around line 80-100)

# =============================================================================
# User Profile Extended Schemas (NEW)
# =============================================================================

class UserProfileOut(BaseModel):
    """Extended user profile output for dashboard and profile pages"""
    user_uid: str
    user_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = None
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    city_id: Optional[int] = None
    city_name: Optional[str] = None
    role: int
    role_name: str
    email_verified: bool = False
    mobile_verified: bool = False
    is_suspended: bool = False
    suspension_reason: Optional[str] = None
    suspension_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    preferences: Optional[dict] = None
    stats: Optional[dict] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = Field(None, max_length=10)
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


class UserDetailOut(UserProfileOut):
    """Extended user details for admin with additional fields"""
    statistics: Optional[dict] = None
    recent_posts: Optional[List[dict]] = None
    admin_info: Optional[dict] = None
    
    class Config:
        from_attributes = True
        

# Add these after your existing User schemas (around line 80-100)

# =============================================================================
# User Profile Extended Schemas (NEW)
# =============================================================================

class UserProfileOut(BaseModel):
    """Extended user profile output for dashboard and profile pages"""
    user_uid: str
    user_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = None
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    city_id: Optional[int] = None
    city_name: Optional[str] = None
    role: int
    role_name: str
    email_verified: bool = False
    mobile_verified: bool = False
    is_suspended: bool = False
    suspension_reason: Optional[str] = None
    suspension_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    preferences: Optional[dict] = None
    stats: Optional[dict] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = Field(None, max_length=10)
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None


class UserDetailOut(UserProfileOut):
    """Extended user details for admin with additional fields"""
    statistics: Optional[dict] = None
    recent_posts: Optional[List[dict]] = None
    admin_info: Optional[dict] = None
    
    class Config:
        from_attributes = True
        
# Add these after your existing User schemas

# =============================================================================
# User Profile Schemas (Minimal)
# =============================================================================

class UserProfileOut(BaseModel):
    """User profile output (without heavy stats)"""
    user_uid: str
    user_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
    role: int
    email_verified: bool = False
    mobile_verified: bool = False
    is_suspended: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    date_of_birth: Optional[datetime] = None
    language: Optional[str] = Field(None, max_length=10)
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    city_id: Optional[int] = None
# Add to schemas.py

# =============================================================================
# Insights Schemas
# =============================================================================

class InsightPageCreate(BaseModel):
    """Schema for creating an insight page."""
    page_number: int
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class InsightPageCreateWithFile(BaseModel):
    """Schema for creating an insight page with file upload support."""
    page_number: int
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_file: Optional[UploadFile] = None


class InsightPageOut(BaseModel):
    """Output schema for insight page."""
    id: int
    page_number: int
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightStoryCreate(BaseModel):
    """Schema for creating/updating an insight story."""
    insight_uid: Optional[str] = None  # Auto-generated if not provided
    title: str
    cover_image_url: Optional[str] = None
    category_name: str
    pages: List[InsightPageCreate]


class InsightStoryCreateWithFiles(BaseModel):
    """Schema for creating/updating an insight story with file upload support."""
    insight_uid: Optional[str] = None  # Auto-generated if not provided
    title: str
    cover_image_url: Optional[str] = None
    category_name: str
    pages: List[InsightPageCreate]
    cover_image_file: Optional[UploadFile] = None


class InsightCoverOut(BaseModel):
    """Output schema for insight cover (grid view)."""
    id: int
    insight_uid: str
    title: str
    cover_image_url: Optional[str] = None
    category_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightStoryOut(BaseModel):
    """Output schema for full insight story."""
    id: int
    insight_uid: str
    title: str
    cover_image_url: Optional[str] = None
    category_name: str
    created_at: datetime
    pages: List[InsightPageOut]

    model_config = ConfigDict(from_attributes=True)


class InsightShareCreate(BaseModel):
    """Schema for creating an insight share."""
    insight_uid: str
    user_uid: str
    platform: str

