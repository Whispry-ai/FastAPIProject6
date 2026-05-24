# from datetime import datetime, timedelta
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session
# from sqlalchemy import or_, func, desc
# from models.content import Advertisement, SponsoredPost, Event, Poll, YouTubeShort
# from models.engagement import Notification
# from database import get_db
# from schemas import (
#     AdvertisementCreate, AdvertisementOut, EventOut, PollDetailOut, 
#     PollOut, PollVote, SponsoredPostCreate, EventCreate, PollCreate, 
#     NewsShortCreate, SponsoredPostOut
# )
# from models.content import (
#     Advertisement, SponsoredPost, Event, Poll, 
#     ContentSchedule, FlaggedContent, ContentTag, ContentTagMapping, ContentVersion
# )
# from schemas import (
#     ScheduledContentCreate, ScheduledContentOut,
#     FlaggedContentCreate, FlaggedContentOut, FlaggedContentReview,
#     TagCreate, TagOut, ContentTagsUpdate, TaggedContentOut,
#     ContentVersionOut, ContentAnalyticsOut, ContentExpiryUpdate,
#     ExpiringContentOut, BulkOperation, BulkOperationResponse,
#     ContentSearchResults, RelatedContentOut, RelatedContentCreate,
#     ContentTemplateCreate, ContentTemplateOut, ReviewQueueOut,
#     ContentAnalyticsOverviewOut, DailyReportOut, MonthlyReportOut
    
# )
# from datetime import datetime, timedelta
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session
# from sqlalchemy import or_, and_, func, desc
# from auth.dependencies import require_role
# from database import get_db
# from models.base_location import State, District, City, Language
# from models.user import User, UserRole, UserPreference
# from models.content import Advertisement, SponsoredPost
# from schemas import AdvertisementCreate, AdvertisementOut, SponsoredPostCreate, SponsoredPostOut, AdTargeting
# from utility import generate_news_uid
# from utility import generate_event_uid, generate_poll_uid
# from models.user import User, UserRole, UserPreference
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, and_
from auth.dependencies import require_role
from database import get_db
from models.base_location import State, District, City, Language
from models.user import User, UserPreference
from schemas import PaginatedAdvertisementsOut, PaginatedSponsoredPostsOut, UserRole  # ✅ Import UserRole from schemas
from models.content import (
    AdImpression, Advertisement, SponsoredImpression, SponsoredPost, Event, Poll, YouTubeShort,
    ContentSchedule, FlaggedContent, ContentTag, ContentTagMapping,
    ContentVersion
)
from schemas import (
    AdvertisementCreate, AdvertisementOut, EventOut, PollDetailOut,
    PollOut, PollVote, SponsoredPostCreate, EventCreate, PollCreate,
    NewsShortCreate, SponsoredPostOut,
    ScheduledContentCreate, ScheduledContentOut,
    FlaggedContentCreate, FlaggedContentOut, FlaggedContentReview,
    TagCreate, TagOut, ContentTagsUpdate, TaggedContentOut,
    ContentVersionOut, ContentAnalyticsOut, ContentExpiryUpdate,
    ExpiringContentOut, BulkOperation, BulkOperationResponse,
    ContentSearchResults, RelatedContentOut, RelatedContentCreate,
    ContentTemplateCreate, ContentTemplateOut, ReviewQueueOut,
    ContentAnalyticsOverviewOut, DailyReportOut, MonthlyReportOut,
    AdTargeting  # ✅ Add AdTargeting if you have it
)
from utility import generate_event_uid, generate_poll_uid

 # Or "/content" depending on your setup
router = APIRouter(prefix="/content", tags=["Content"])




# =============================
# Events
# =============================

@router.post(
    "/events", 
    response_model=EventOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create event"
)
def create_event(
    event: EventCreate, 
    db: Session = Depends(get_db)
):
    """Create a new event (Requires approval)"""
    event_data = event.dict()
    event_data["event_uid"] = generate_event_uid()
    event_data["is_approved"] = False  # Default to not approved
    
    new_event = Event(**event_data)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.get(
    "/events", 
    response_model=List[EventOut],
    summary="Get all approved events"
)
def get_all_approved_events(
    search: Optional[str] = Query(None, description="Search by title or location"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    is_online: Optional[bool] = Query(None, description="Filter by online/offline"),
    upcoming_only: bool = Query(True, description="Show only upcoming events"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all approved events with optional filters"""
    query = db.query(Event).filter(Event.is_approved == True)
    
    if upcoming_only:
        query = query.filter(Event.event_date >= datetime.utcnow().date())
    
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.location.ilike(f"%{search}%")
            )
        )
    
    if state_id:
        query = query.filter(Event.state_id == state_id)
    
    if district_id:
        query = query.filter(Event.district_id == district_id)
    
    if city_id:
        query = query.filter(Event.city_id == city_id)
    
    if is_online is not None:
        query = query.filter(Event.is_online == is_online)
    
    query = query.order_by(Event.event_date.asc()).offset(offset).limit(limit)
    return query.all()


@router.get(
    "/events/{event_uid}", 
    response_model=EventOut,
    summary="Get event by UID"
)
def get_event_by_uid(
    event_uid: str,
    db: Session = Depends(get_db)
):
    """Get event details by UID"""
    event = db.query(Event).filter(Event.event_uid == event_uid).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get(
    "/admin/events/pending", 
    response_model=List[EventOut],
    summary="Get pending events"
)
def get_pending_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all events pending approval (Admin only)"""
    return db.query(Event)\
        .filter(Event.is_approved == False)\
        .order_by(Event.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()


@router.put(
    "/admin/events/{event_id}/approval", 
    status_code=status.HTTP_200_OK,
    summary="Approve/reject event"
)
def approve_event(
    event_id: int, 
    status: bool = Query(..., description="True to approve, False to reject"),
    rejection_reason: Optional[str] = Query(None, description="Reason for rejection"),
    db: Session = Depends(get_db)
):
    """Approve or reject an event (Admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
    
    event.is_approved = status
    event.approved_at = datetime.utcnow() if status else None
    event.rejection_reason = rejection_reason if not status else None
    
    db.commit()
    return {"message": f"Event {'approved' if status else 'rejected'} successfully"}


@router.put(
    "/events/{event_id}", 
    response_model=EventOut,
    summary="Update event"
)
def update_event(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Update event details (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    
    db_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete(
    "/events/{event_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete event"
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Delete an event (Admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    return None


# =============================
# Polls
# =============================

@router.post(
    "/polls", 
    response_model=PollCreate, 
    status_code=status.HTTP_201_CREATED,
    summary="Create poll"
)
def create_poll(
    poll: PollCreate, 
    db: Session = Depends(get_db)
):
    """Create a new poll"""
    if len(poll.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="At least 2 options required"
        )
    
    if len(poll.options) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Maximum 10 options allowed"
        )
    
    new_poll = Poll(
        poll_uid=generate_poll_uid(),
        question=poll.question,
        options=poll.options,
        votes=[0] * len(poll.options),
        expires_at=poll.expires_at,
        is_approved=False  # Default to not approved
    )
    db.add(new_poll)
    db.commit()
    db.refresh(new_poll)
    return new_poll


@router.put(
    "/polls/vote", 
    status_code=status.HTTP_200_OK,
    summary="Vote in poll"
)
def vote_poll(
    vote: PollVote, 
    db: Session = Depends(get_db)
):
    """Vote in a poll"""
    poll = db.query(Poll).filter(Poll.poll_uid == vote.poll_uid).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Poll not found"
        )
    
    # Check if poll is approved
    if not poll.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Poll is not approved yet"
        )
    
    # Expiration check
    if poll.expires_at and datetime.utcnow() > poll.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Poll has expired"
        )
    
    # Duplicate vote check
    if vote.user_uid in (poll.user_uids_voted or []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already voted"
        )
    
    # Option index validation
    if vote.option_index >= len(poll.votes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid option index"
        )
    
    # Record vote
    poll.votes[vote.option_index] += 1
    updated_users = poll.user_uids_voted or []
    updated_users.append(vote.user_uid)
    poll.user_uids_voted = updated_users
    
    db.commit()
    db.refresh(poll)
    
    return {"message": "Vote recorded successfully"}


@router.get(
    "/polls/active", 
    response_model=List[PollOut],
    summary="Get active polls"
)
def get_active_polls(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all active (approved and not expired) polls"""
    current_time = datetime.utcnow()
    active_polls = db.query(Poll).filter(
        Poll.is_approved == True,
        (Poll.expires_at == None) | (Poll.expires_at > current_time)
    ).order_by(Poll.created_at.desc()).offset(offset).limit(limit).all()
    return active_polls


@router.get(
    "/polls/{poll_uid}", 
    response_model=PollDetailOut,
    summary="Get poll details"
)
def get_poll_details(
    poll_uid: str, 
    db: Session = Depends(get_db)
):
    """Get poll details by UID"""
    poll = db.query(Poll).filter(Poll.poll_uid == poll_uid).first()
    
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Poll not found"
        )
    
    # Optional: Filter out expired polls if needed
    if poll.expires_at and datetime.utcnow() > poll.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Poll has expired"
        )
    
    return poll


@router.get(
    "/admin/polls/pending", 
    response_model=List[PollOut],
    summary="Get pending polls"
)
def get_pending_polls(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all polls pending approval (Admin only)"""
    return db.query(Poll)\
        .filter(Poll.is_approved == False)\
        .order_by(Poll.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()


@router.put(
    "/admin/polls/{poll_id}/approval", 
    status_code=status.HTTP_200_OK,
    summary="Approve/reject poll"
)
def approve_poll(
    poll_id: int,
    status: bool = Query(..., description="True to approve, False to reject"),
    db: Session = Depends(get_db)
):
    """Approve or reject a poll (Admin only)"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    poll.is_approved = status
    poll.approved_at = datetime.utcnow() if status else None
    
    db.commit()
    return {"message": f"Poll {'approved' if status else 'rejected'} successfully"}


@router.put(
    "/polls/{poll_id}", 
    response_model=PollCreate,
    summary="Update poll"
)
def update_poll(
    poll_id: int,
    poll: PollCreate,
    db: Session = Depends(get_db)
):
    """Update poll details (Admin only)"""
    db_poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not db_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    if len(poll.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 options required"
        )
    
    db_poll.question = poll.question
    db_poll.options = poll.options
    db_poll.votes = [0] * len(poll.options)
    db_poll.expires_at = poll.expires_at
    db_poll.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_poll)
    return db_poll


@router.delete(
    "/polls/{poll_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete poll"
)
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db)
):
    """Delete a poll (Admin only)"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    db.delete(poll)
    db.commit()
    return None


# =============================
# YouTube Shorts
# =============================

@router.post(
    "/news-shorts", 
    response_model=NewsShortCreate,
    status_code=status.HTTP_201_CREATED,
    summary="Create news short"
)
def create_news_short(
    short: NewsShortCreate,
    db: Session = Depends(get_db)
):
    """Create a new YouTube news short"""
    existing = db.query(YouTubeShort).filter(
        YouTubeShort.video_id == short.video_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Short with this video ID already exists"
        )
    
    new_short = YouTubeShort(**short.dict())
    db.add(new_short)
    db.commit()
    db.refresh(new_short)
    return new_short


@router.get(
    "/news-shorts", 
    response_model=List[NewsShortCreate],
    summary="Get news shorts"
)
def get_news_shorts(
    language: str = Query(..., description="Language code like 'en' or 'te'"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get news shorts by language"""
    return db.query(YouTubeShort)\
        .filter(YouTubeShort.language == language)\
        .order_by(YouTubeShort.published_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()


# =============================
# Statistics
# =============================

@router.get(
    "/stats", 
    summary="Get content statistics"
)
def get_content_stats(
    db: Session = Depends(get_db)
):
    """Get statistics for all content types"""
    current_time = datetime.utcnow()
    
    return {
        "sponsored_posts": {
            "total": db.query(SponsoredPost).count(),
            "approved": db.query(SponsoredPost).filter(SponsoredPost.is_approved == True).count(),
            "pending": db.query(SponsoredPost).filter(SponsoredPost.is_approved == False).count()
        },
        "advertisements": {
            "total": db.query(Advertisement).count(),
            "active": db.query(Advertisement).filter(
                Advertisement.is_active == True,
                Advertisement.start_date <= current_time,
                Advertisement.end_date >= current_time
            ).count()
        },
        "events": {
            "total": db.query(Event).count(),
            "approved": db.query(Event).filter(Event.is_approved == True).count(),
            "pending": db.query(Event).filter(Event.is_approved == False).count(),
            "upcoming": db.query(Event).filter(
                Event.is_approved == True,
                Event.event_date >= current_time.date()
            ).count()
        },
        "polls": {
            "total": db.query(Poll).count(),
            "approved": db.query(Poll).filter(Poll.is_approved == True).count(),
            "pending": db.query(Poll).filter(Poll.is_approved == False).count(),
            "active": db.query(Poll).filter(
                Poll.is_approved == True,
                (Poll.expires_at == None) | (Poll.expires_at > current_time)
            ).count()
        }
    }
    


# =============================
# Content Scheduling APIs
# =============================

@router.post(
    "/admin/content/schedule",
    response_model=ScheduledContentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin", "Scheduling"]
)
def schedule_content(
    schedule: ScheduledContentCreate,
    db: Session = Depends(get_db)
):
    """Schedule content for future publishing (Admin only)"""
    # Check if content exists
    content_model = get_content_model(schedule.content_type)
    if not content_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {schedule.content_type}"
        )
    
    content = db.query(content_model).filter(
        content_model.id == schedule.content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{schedule.content_type} with id {schedule.content_id} not found"
        )
    
    # Check if already scheduled
    existing = db.query(ContentSchedule).filter(
        ContentSchedule.content_type == schedule.content_type,
        ContentSchedule.content_id == schedule.content_id,
        ContentSchedule.status == "pending"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content already scheduled"
        )
    
    new_schedule = ContentSchedule(**schedule.dict())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get(
    "/admin/content/scheduled",
    response_model=List[ScheduledContentOut],
    tags=["Admin", "Scheduling"]
)
def get_scheduled_content(
    status: Optional[str] = Query(None, enum=["pending", "published", "failed"]),
    content_type: Optional[str] = Query(None, enum=["sponsored_post", "advertisement", "event", "poll"]),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all scheduled content"""
    query = db.query(ContentSchedule)
    
    if status:
        query = query.filter(ContentSchedule.status == status)
    if content_type:
        query = query.filter(ContentSchedule.content_type == content_type)
    if from_date:
        query = query.filter(ContentSchedule.scheduled_at >= from_date)
    if to_date:
        query = query.filter(ContentSchedule.scheduled_at <= to_date)
    
    return query.order_by(ContentSchedule.scheduled_at.asc()).offset(offset).limit(limit).all()


@router.delete(
    "/admin/content/schedule/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin", "Scheduling"]
)
def cancel_scheduled_content(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Cancel scheduled content"""
    schedule = db.query(ContentSchedule).filter(ContentSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    
    if schedule.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel non-pending schedule")
    
    db.delete(schedule)
    db.commit()
    return None


# =============================
# Content Flagging/Moderation APIs
# =============================

@router.post(
    "/{content_type}/{content_id}/flag",
    response_model=FlaggedContentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Moderation"]
)
def flag_content(
    content_type: str,
    content_id: int,
    flag: FlaggedContentCreate,
    db: Session = Depends(get_db)
):
    """Flag content for review by users"""
    # Check if already flagged
    existing = db.query(FlaggedContent).filter(
        FlaggedContent.content_type == content_type,
        FlaggedContent.content_id == content_id,
        FlaggedContent.flagged_by == flag.flagged_by,
        FlaggedContent.status == "pending"
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already flagged this content")
    
    new_flag = FlaggedContent(
        content_type=content_type,
        content_id=content_id,
        flagged_by=flag.flagged_by,
        reason=flag.reason
    )
    db.add(new_flag)
    db.commit()
    db.refresh(new_flag)
    return new_flag


@router.get(
    "/admin/content/flagged",
    response_model=List[FlaggedContentOut],
    tags=["Admin", "Moderation"]
)
def get_flagged_content(
    status: str = Query("pending", enum=["pending", "reviewed", "dismissed"]),
    content_type: Optional[str] = Query(None, enum=["sponsored_post", "advertisement", "event", "poll"]),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get flagged content for review (Admin only)"""
    query = db.query(FlaggedContent).filter(FlaggedContent.status == status)
    
    if content_type:
        query = query.filter(FlaggedContent.content_type == content_type)
    
    return query.order_by(desc(FlaggedContent.created_at)).offset(offset).limit(limit).all()


@router.post(
    "/admin/content/flagged/{flag_id}/review",
    response_model=FlaggedContentOut,
    tags=["Admin", "Moderation"]
)
def review_flagged_content(
    flag_id: int,
    review: FlaggedContentReview,
    db: Session = Depends(get_db)
):
    """Review and take action on flagged content (Admin only)"""
    flag = db.query(FlaggedContent).filter(FlaggedContent.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found")
    
    flag.status = "reviewed" if review.action == "approve" else "dismissed"
    flag.review_notes = review.review_notes
    
    # If action is reject, hide the content
    if review.action == "reject":
        content_model = get_content_model(flag.content_type)
        if content_model:
            content = db.query(content_model).filter(content_model.id == flag.content_id).first()
            if content:
                if hasattr(content, 'is_approved'):
                    content.is_approved = False
                elif hasattr(content, 'is_active'):
                    content.is_active = False
    
    db.commit()
    db.refresh(flag)
    return flag


# =============================
# Content Tags APIs
# =============================

@router.post(
    "/admin/tags",
    response_model=TagOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin", "Tags"]
)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """Create a new content tag (Admin only)"""
    existing = db.query(ContentTag).filter(
        func.lower(ContentTag.name) == func.lower(tag.name)
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    
    new_tag = ContentTag(name=tag.name.lower())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get(
    "/tags",
    response_model=List[TagOut],
    tags=["Tags"]
)
def get_tags(
    search: Optional[str] = Query(None, min_length=2),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get all tags"""
    query = db.query(ContentTag)
    
    if search:
        query = query.filter(ContentTag.name.ilike(f"%{search}%"))
    
    return query.order_by(desc(ContentTag.usage_count)).limit(limit).all()


@router.post(
    "/{content_type}/{content_id}/tags",
    status_code=status.HTTP_200_OK,
    tags=["Tags"]
)
def assign_tags(
    content_type: str,
    content_id: int,
    tags_data: ContentTagsUpdate,
    db: Session = Depends(get_db)
):
    """Assign tags to content"""
    # Remove existing tags
    db.query(ContentTagMapping).filter(
        ContentTagMapping.content_type == content_type,
        ContentTagMapping.content_id == content_id
    ).delete()
    
    # Add new tags
    for tag_name in tags_data.tags:
        tag = db.query(ContentTag).filter(
            func.lower(ContentTag.name) == func.lower(tag_name)
        ).first()
        
        if not tag:
            tag = ContentTag(name=tag_name.lower())
            db.add(tag)
            db.flush()
        
        # Update usage count
        tag.usage_count += 1
        
        # Create mapping
        mapping = ContentTagMapping(
            content_type=content_type,
            content_id=content_id,
            tag_id=tag.id
        )
        db.add(mapping)
    
    db.commit()
    return {"message": "Tags assigned successfully"}


@router.get(
    "/tags/{tag_name}/content",
    response_model=List[TaggedContentOut],
    tags=["Tags"]
)
def get_content_by_tag(
    tag_name: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get all content with a specific tag"""
    tag = db.query(ContentTag).filter(
        func.lower(ContentTag.name) == func.lower(tag_name)
    ).first()
    
    if not tag:
        return []
    
    mappings = db.query(ContentTagMapping).filter(
        ContentTagMapping.tag_id == tag.id
    ).limit(limit).all()
    
    results = []
    for mapping in mappings:
        results.append({
            "id": mapping.id,
            "content_type": mapping.content_type,
            "content_id": mapping.content_id,
            "tag": tag
        })
    
    return results


# =============================
# Content Expiry Management APIs
# =============================

@router.post(
    "/admin/{content_type}/{content_id}/expire",
    status_code=status.HTTP_200_OK,
    tags=["Admin", "Expiry"]
)
def set_content_expiry(
    content_type: str,
    content_id: int,
    expiry: ContentExpiryUpdate,
    db: Session = Depends(get_db)
):
    """Set expiration date for content (Admin only)"""
    content_model = get_content_model(content_type)
    if not content_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type")
    
    content = db.query(content_model).filter(content_model.id == content_id).first()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    
    if hasattr(content, 'expires_at'):
        content.expires_at = expiry.expires_at
    elif hasattr(content, 'end_date'):
        content.end_date = expiry.expires_at
    
    db.commit()
    return {"message": "Expiry date set successfully"}


@router.get(
    "/admin/content/expiring-soon",
    response_model=List[ExpiringContentOut],
    tags=["Admin", "Expiry"]
)
def get_expiring_content(
    days: int = Query(7, ge=1, le=30),
    content_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get content expiring within specified days (Admin only)"""
    current_time = datetime.utcnow()
    expiry_threshold = current_time + timedelta(days=days)
    
    results = []
    
    # Check sponsored posts
    if not content_type or content_type == "sponsored_post":
        posts = db.query(SponsoredPost).filter(
            SponsoredPost.end_date.between(current_time, expiry_threshold)
        ).all()
        for post in posts:
            results.append({
                "content_type": "sponsored_post",
                "content_id": post.id,
                "title": post.title,
                "expires_at": post.end_date,
                "days_until_expiry": (post.end_date - current_time).days
            })
    
    # Check advertisements
    if not content_type or content_type == "advertisement":
        ads = db.query(Advertisement).filter(
            Advertisement.end_date.between(current_time, expiry_threshold)
        ).all()
        for ad in ads:
            results.append({
                "content_type": "advertisement",
                "content_id": ad.id,
                "title": ad.title,
                "expires_at": ad.end_date,
                "days_until_expiry": (ad.end_date - current_time).days
            })
    
    # Check polls
    if not content_type or content_type == "poll":
        polls = db.query(Poll).filter(
            Poll.expires_at.isnot(None),
            Poll.expires_at.between(current_time, expiry_threshold)
        ).all()
        for poll in polls:
            results.append({
                "content_type": "poll",
                "content_id": poll.id,
                "title": poll.question[:50],
                "expires_at": poll.expires_at,
                "days_until_expiry": (poll.expires_at - current_time).days
            })
    
    return sorted(results, key=lambda x: x['days_until_expiry'])


# =============================
# Content Analytics APIs
# =============================

@router.get(
    "/analytics/{content_type}/{content_id}",
    response_model=ContentAnalyticsOut,
    tags=["Analytics"]
)
def get_content_analytics(
    content_type: str,
    content_id: int,
    period_days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get analytics for specific content"""
    # This would typically query an analytics table
    # For now, return mock data structure
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    return {
        "content_type": content_type,
        "content_id": content_id,
        "views": 0,
        "clicks": 0,
        "engagement_rate": 0.0,
        "total_interactions": 0,
        "period_start": start_date,
        "period_end": end_date,
        "daily_breakdown": []
    }


@router.get(
    "/admin/analytics/overview",
    response_model=ContentAnalyticsOverviewOut,
    tags=["Admin", "Analytics"]
)
def get_analytics_overview(
    db: Session = Depends(get_db)
):
    """Get overview of content analytics (Admin only)"""
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    return {
        "total_content": {
            "sponsored_posts": db.query(SponsoredPost).count(),
            "advertisements": db.query(Advertisement).count(),
            "events": db.query(Event).count(),
            "polls": db.query(Poll).count()
        },
        "published_today": {
            "sponsored_posts": db.query(SponsoredPost).filter(func.date(SponsoredPost.created_at) == today).count(),
            "advertisements": db.query(Advertisement).filter(func.date(Advertisement.created_at) == today).count(),
            "events": db.query(Event).filter(func.date(Event.created_at) == today).count(),
            "polls": db.query(Poll).filter(func.date(Poll.created_at) == today).count()
        },
        "published_this_week": {
            "sponsored_posts": db.query(SponsoredPost).filter(SponsoredPost.created_at >= week_start).count(),
            "advertisements": db.query(Advertisement).filter(Advertisement.created_at >= week_start).count(),
            "events": db.query(Event).filter(Event.created_at >= week_start).count(),
            "polls": db.query(Poll).filter(Poll.created_at >= week_start).count()
        },
        "published_this_month": {
            "sponsored_posts": db.query(SponsoredPost).filter(SponsoredPost.created_at >= month_start).count(),
            "advertisements": db.query(Advertisement).filter(Advertisement.created_at >= month_start).count(),
            "events": db.query(Event).filter(Event.created_at >= month_start).count(),
            "polls": db.query(Poll).filter(Poll.created_at >= month_start).count()
        },
        "pending_approval": {
            "sponsored_posts": db.query(SponsoredPost).filter(SponsoredPost.is_approved == False).count(),
            "events": db.query(Event).filter(Event.is_approved == False).count(),
            "polls": db.query(Poll).filter(Poll.is_approved == False).count()
        },
        "top_performing": [],
        "engagement_trends": {}
    }


# =============================
# Bulk Operations APIs
# =============================

@router.post(
    "/admin/bulk/approve",
    response_model=BulkOperationResponse,
    tags=["Admin", "Bulk"]
)
def bulk_approve_content(
    operation: BulkOperation,
    db: Session = Depends(get_db)
):
    """Bulk approve content (Admin only)"""
    results = {"total": len(operation.content_ids), "successful": 0, "failed": 0, "errors": []}
    
    for content_id in operation.content_ids:
        try:
            content = db.query(SponsoredPost).filter(SponsoredPost.id == content_id).first()
            if content:
                content.is_approved = True
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"id": content_id, "error": "Content not found"})
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"id": content_id, "error": str(e)})
    
    db.commit()
    return results


@router.post(
    "/admin/bulk/delete",
    response_model=BulkOperationResponse,
    tags=["Admin", "Bulk"]
)
def bulk_delete_content(
    operation: BulkOperation,
    db: Session = Depends(get_db)
):
    """Bulk delete content (Admin only)"""
    results = {"total": len(operation.content_ids), "successful": 0, "failed": 0, "errors": []}
    
    for content_id in operation.content_ids:
        try:
            # Try to delete from all content types
            content = db.query(SponsoredPost).filter(SponsoredPost.id == content_id).first()
            if not content:
                content = db.query(Advertisement).filter(Advertisement.id == content_id).first()
            if not content:
                content = db.query(Event).filter(Event.id == content_id).first()
            if not content:
                content = db.query(Poll).filter(Poll.id == content_id).first()
            
            if content:
                db.delete(content)
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"id": content_id, "error": "Content not found"})
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"id": content_id, "error": str(e)})
    
    db.commit()
    return results


# =============================
# Content Search API
# =============================

@router.get(
    "/search",
    response_model=ContentSearchResults,
    tags=["Search"]
)
def search_content(
    query: str = Query(..., min_length=2),
    content_type: Optional[str] = Query(None, enum=["sponsored", "advertisement", "event", "poll"]),
    status: Optional[str] = Query(None, enum=["approved", "pending"]),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search across all content types"""
    results = []
    
    # Search sponsored posts
    if not content_type or content_type == "sponsored":
        sponsored = db.query(SponsoredPost).filter(
            or_(
                SponsoredPost.title.ilike(f"%{query}%"),
                SponsoredPost.content.ilike(f"%{query}%")
            )
        )
        if status == "approved":
            sponsored = sponsored.filter(SponsoredPost.is_approved == True)
        elif status == "pending":
            sponsored = sponsored.filter(SponsoredPost.is_approved == False)
        
        for item in sponsored.limit(limit).all():
            results.append({
                "type": "sponsored_post",
                "id": item.id,
                "title": item.title,
                "created_at": item.created_at,
                "is_approved": item.is_approved
            })
    
    # Search events
    if not content_type or content_type == "event":
        events = db.query(Event).filter(
            or_(
                Event.title.ilike(f"%{query}%"),
                Event.description.ilike(f"%{query}%"),
                Event.location.ilike(f"%{query}%")
            )
        )
        if status == "approved":
            events = events.filter(Event.is_approved == True)
        elif status == "pending":
            events = events.filter(Event.is_approved == False)
        
        for item in events.limit(limit).all():
            results.append({
                "type": "event",
                "id": item.id,
                "title": item.title,
                "created_at": item.created_at,
                "is_approved": item.is_approved
            })
    
    total = len(results)
    results = results[offset:offset + limit]
    
    return {
        "total": total,
        "items": results,
        "page": offset // limit + 1 if limit > 0 else 1,
        "limit": limit,
        "has_next": len(results) == limit,
        "has_previous": offset > 0
    }


# =============================
# Helper Function
# =============================

def get_content_model(content_type: str):
    """Map content type to SQLAlchemy model"""
    mapping = {
        "sponsored_post": SponsoredPost,
        "advertisement": Advertisement,
        "event": Event,
        "poll": Poll
    }
    return mapping.get(content_type)





# =========================================================
# HELPER FUNCTIONS
# =========================================================

def apply_targeting_filters(query, targeting: AdTargeting, db: Session):
    """Apply targeting filters to query"""
    
    # Location filters
    if targeting.cities:
        query = query.filter(Advertisement.city_id.in_(targeting.cities))
    elif targeting.districts:
        query = query.filter(Advertisement.district_id.in_(targeting.districts))
    elif targeting.states:
        query = query.filter(Advertisement.state_id.in_(targeting.states))
    
    # Language filter
    if targeting.languages:
        query = query.filter(Advertisement.language_id.in_(targeting.languages))
    
    # Gender filter
    if targeting.gender and targeting.gender != "all":
        query = query.filter(Advertisement.target_gender == targeting.gender)
    
    # Age filter
    if targeting.age_min is not None:
        query = query.filter(Advertisement.target_age_min <= targeting.age_min)
    if targeting.age_max is not None:
        query = query.filter(Advertisement.target_age_max >= targeting.age_max)
    
    return query


def get_targeting_priority(user_pref, db: Session):
    """Get targeting priority levels based on user preferences"""
    targeting = {
        "city_id": user_pref.city_id if user_pref else None,
        "district_id": user_pref.district_id if user_pref else None,
        "state_id": user_pref.state_id if user_pref else None,
        "language_id": user_pref.language_id if user_pref else None
    }
    return targeting


def calculate_ad_score(ad, user_pref):
    """Calculate relevance score for ad based on user preferences"""
    score = 0
    
    if user_pref:
        # Location match (higher weight for closer location)
        if ad.city_id and ad.city_id == user_pref.city_id:
            score += 100
        elif ad.district_id and ad.district_id == user_pref.district_id:
            score += 50
        elif ad.state_id and ad.state_id == user_pref.state_id:
            score += 25
        
        # Language match
        if ad.language_id and ad.language_id == user_pref.language_id:
            score += 40
        
        # Gender match
        if ad.target_gender and ad.target_gender == user_pref.gender:
            score += 20
    
    return score
# =========================================================
# HELPER FUNCTIONS (Add after calculate_ad_score function)
# =========================================================

def get_active_ads_helper(
    user_uid: Optional[str] = None,
    placement: str = "feed",
    limit: int = 10,
    session_id: Optional[str] = None,
    include_premium: bool = True,
    premium_limit: int = 1,
    exclude_seen: bool = True,
    db: Session = None,
) -> dict:
    """
    Helper function to get active advertisements with targeting.
    Used by both API endpoint and news feed.
    """
    from datetime import datetime
    from sqlalchemy import or_, desc
    import random
    
    current_time = datetime.utcnow()
    
    # Base query: active and approved ads
    query = db.query(Advertisement).filter(
        Advertisement.is_active == True,
        Advertisement.is_approved == True,
        Advertisement.start_date <= current_time,
        Advertisement.end_date >= current_time
    )
    
    if placement:
        query = query.filter(Advertisement.placement == placement)
    
    # Get user preferences for targeting
    user_pref = None
    if user_uid:
        user_pref = db.query(UserPreference).filter(
            UserPreference.user_uid == user_uid
        ).first()
        
        # Also get user's location from user table if preferences not set
        if not user_pref:
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if user:
                class TempPref:
                    pass
                user_pref = TempPref()
                user_pref.city_id = user.city_id
                user_pref.district_id = user.district_id
                user_pref.state_id = user.state_id
                user_pref.language_id = None
                user_pref.gender = user.gender
    
    # Track seen ads in this session
    seen_ids = set()
    if exclude_seen and session_id:
        try:
            from models.engagement import AdImpression
            seen_ads = db.query(AdImpression.ad_id).filter(
                AdImpression.session_id == session_id
            ).all()
            seen_ids = {ad[0] for ad in seen_ads}
        except Exception as e:
            print(f"Error querying AdImpression: {e}")
    
    all_ads = []
    
    # =========================================================
    # PRIORITY 0: PREMIUM ADS
    # =========================================================
    if include_premium:
        premium_query = query.filter(Advertisement.is_premium == True)
        
        if user_pref:
            location_conditions = []
            if hasattr(user_pref, 'city_id') and user_pref.city_id:
                location_conditions.append(Advertisement.city_id == user_pref.city_id)
            if hasattr(user_pref, 'district_id') and user_pref.district_id:
                location_conditions.append(Advertisement.district_id == user_pref.district_id)
            if hasattr(user_pref, 'state_id') and user_pref.state_id:
                location_conditions.append(Advertisement.state_id == user_pref.state_id)
            
            if location_conditions:
                premium_query = premium_query.filter(or_(*location_conditions))
        
        premium_ads = premium_query.order_by(
            desc(Advertisement.premium_priority),
            desc(Advertisement.created_at)
        ).all()
        
        premium_ads = [ad for ad in premium_ads if ad.id not in seen_ids]
        
        for idx, ad in enumerate(premium_ads):
            ad.priority = "premium"
            ad.priority_level = 0
            ad.cpm_multiplier = 3.0
            ad.premium_rank = idx + 1
        
        all_ads.extend(premium_ads[:premium_limit])
        for ad in premium_ads[:premium_limit]:
            seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 1: CITY ADS
    # =========================================================
    if len(all_ads) < limit and user_pref and hasattr(user_pref, 'city_id') and user_pref.city_id:
        city_ads = query.filter(
            Advertisement.city_id == user_pref.city_id,
            Advertisement.is_premium == False
        )
        
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            city_ads = city_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in city_ads.all():
            if ad.id not in seen_ids:
                ad.priority = "city"
                ad.priority_level = 1
                ad.cpm_multiplier = 2.0
                all_ads.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 2: DISTRICT ADS
    # =========================================================
    if len(all_ads) < limit and user_pref and hasattr(user_pref, 'district_id') and user_pref.district_id:
        district_ads = query.filter(
            Advertisement.district_id == user_pref.district_id,
            Advertisement.is_premium == False,
            Advertisement.city_id == None
        )
        
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            district_ads = district_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in district_ads.all():
            if ad.id not in seen_ids:
                ad.priority = "district"
                ad.priority_level = 2
                ad.cpm_multiplier = 1.5
                all_ads.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 3: STATE ADS
    # =========================================================
    if len(all_ads) < limit and user_pref and hasattr(user_pref, 'state_id') and user_pref.state_id:
        state_ads = query.filter(
            Advertisement.state_id == user_pref.state_id,
            Advertisement.is_premium == False,
            Advertisement.city_id == None,
            Advertisement.district_id == None
        )
        
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            state_ads = state_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in state_ads.all():
            if ad.id not in seen_ids:
                ad.priority = "state"
                ad.priority_level = 3
                ad.cpm_multiplier = 1.2
                all_ads.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 4: LANGUAGE ADS
    # =========================================================
    if len(all_ads) < limit and user_pref and hasattr(user_pref, 'language_id') and user_pref.language_id:
        lang_ads = query.filter(
            Advertisement.language_id == user_pref.language_id,
            Advertisement.is_premium == False,
            Advertisement.state_id == None,
            Advertisement.district_id == None,
            Advertisement.city_id == None
        )
        
        for ad in lang_ads.all():
            if ad.id not in seen_ids:
                ad.priority = "language"
                ad.priority_level = 4
                ad.cpm_multiplier = 1.0
                all_ads.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 5: NATIONAL ADS
    # =========================================================
    if len(all_ads) < limit:
        national_ads = query.filter(
            Advertisement.is_premium == False,
            Advertisement.state_id == None,
            Advertisement.district_id == None,
            Advertisement.city_id == None
        )
        
        for ad in national_ads.all():
            if ad.id not in seen_ids:
                ad.priority = "national"
                ad.priority_level = 5
                ad.cpm_multiplier = 0.8
                all_ads.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # ROTATE & SORT BY PRIORITY
    # =========================================================
    priority_groups = {}
    for ad in all_ads:
        level = ad.priority_level
        if level not in priority_groups:
            priority_groups[level] = []
        priority_groups[level].append(ad)
    
    for level in priority_groups:
        random.shuffle(priority_groups[level])
    
    final_ads = []
    for level in sorted(priority_groups.keys()):
        final_ads.extend(priority_groups[level])
    
    final_ads = final_ads[:limit]
    
    # Log impressions
    for ad in final_ads:
        try:
            from models.engagement import AdImpression
            impression = AdImpression(
                ad_id=ad.id,
                user_uid=user_uid,
                session_id=session_id,
                impression_at=datetime.utcnow()
            )
            db.add(impression)
        except Exception as e:
            print(f"Error logging impression: {e}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing impressions: {e}")
    
    return {
        "ads": final_ads,
        "metadata": {
            "total_available": len(all_ads),
            "returned": len(final_ads),
            "has_premium": len([a for a in final_ads if a.priority == "premium"]) > 0,
            "premium_count": len([a for a in final_ads if a.priority == "premium"]),
            "priority_breakdown": {
                "premium": len([a for a in final_ads if a.priority == "premium"]),
                "city": len([a for a in final_ads if a.priority == "city"]),
                "district": len([a for a in final_ads if a.priority == "district"]),
                "state": len([a for a in final_ads if a.priority == "state"]),
                "language": len([a for a in final_ads if a.priority == "language"]),
                "national": len([a for a in final_ads if a.priority == "national"])
            }
        }
    }

def get_active_sponsored_posts_helper(
    user_uid: Optional[str] = None,
    limit: int = 10,
    session_id: Optional[str] = None,
    exclude_seen: bool = True,
    db: Session = None,
) -> dict:
    """Helper function to get active sponsored posts with targeting."""
    from datetime import datetime
    from sqlalchemy import or_
    import random
    
    current_time = datetime.utcnow()
    
    query = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= current_time,
        SponsoredPost.end_date >= current_time
    )
    
    # Get user preferences
    user_pref = None
    if user_uid:
        user_pref = db.query(UserPreference).filter(
            UserPreference.user_uid == user_uid
        ).first()
        
        if not user_pref:
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if user:
                class TempPref:
                    pass
                user_pref = TempPref()
                user_pref.city_id = user.city_id
                user_pref.district_id = user.district_id
                user_pref.state_id = user.state_id
                user_pref.language_id = None
    
    # Track seen posts
    seen_ids = set()
    if exclude_seen and session_id:
        try:
            from models.engagement import SponsoredImpression
            seen_posts = db.query(SponsoredImpression.post_id).filter(
                SponsoredImpression.session_id == session_id
            ).all()
            seen_ids = {post[0] for post in seen_posts}
        except Exception:
            pass
    
    results = []
    
    # Priority 1: City targeting
    if user_pref and hasattr(user_pref, 'city_id') and user_pref.city_id:
        city_posts = query.filter(SponsoredPost.city_id == user_pref.city_id)
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            city_posts = city_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in city_posts.all():
            if post.id not in seen_ids:
                post.priority = "city"
                post.priority_level = 1
                results.append(post)
                seen_ids.add(post.id)
    
    # Priority 2: District targeting
    if len(results) < limit and user_pref and hasattr(user_pref, 'district_id') and user_pref.district_id:
        district_posts = query.filter(SponsoredPost.district_id == user_pref.district_id)
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            district_posts = district_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in district_posts.all():
            if post.id not in seen_ids:
                post.priority = "district"
                post.priority_level = 2
                results.append(post)
                seen_ids.add(post.id)
    
    # Priority 3: State targeting
    if len(results) < limit and user_pref and hasattr(user_pref, 'state_id') and user_pref.state_id:
        state_posts = query.filter(SponsoredPost.state_id == user_pref.state_id)
        if hasattr(user_pref, 'language_id') and user_pref.language_id:
            state_posts = state_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in state_posts.all():
            if post.id not in seen_ids:
                post.priority = "state"
                post.priority_level = 3
                results.append(post)
                seen_ids.add(post.id)
    
    # Priority 4: Language targeting
    if len(results) < limit and user_pref and hasattr(user_pref, 'language_id') and user_pref.language_id:
        lang_posts = query.filter(
            SponsoredPost.language_id == user_pref.language_id,
            SponsoredPost.state_id == None,
            SponsoredPost.district_id == None,
            SponsoredPost.city_id == None
        )
        
        for post in lang_posts.all():
            if post.id not in seen_ids:
                post.priority = "language"
                post.priority_level = 4
                results.append(post)
                seen_ids.add(post.id)
    
    # Priority 5: National posts
    if len(results) < limit:
        national_posts = query.filter(
            SponsoredPost.state_id == None,
            SponsoredPost.district_id == None,
            SponsoredPost.city_id == None
        )
        
        for post in national_posts.all():
            if post.id not in seen_ids:
                post.priority = "national"
                post.priority_level = 5
                results.append(post)
                seen_ids.add(post.id)
    
    # Sort by priority
    results.sort(key=lambda x: x.priority_level)
    final_results = results[:limit]
    
    # Log impressions
    for post in final_results:
        try:
            from models.engagement import SponsoredImpression
            impression = SponsoredImpression(
                post_id=post.id,
                user_uid=user_uid,
                session_id=session_id,
                impression_at=datetime.utcnow()
            )
            db.add(impression)
        except Exception:
            pass
    
    try:
        db.commit()
    except Exception:
        db.rollback()
    
    return {
        "posts": final_results,
        "metadata": {
            "total_available": len(results),
            "returned": len(final_results),
            "priority_breakdown": {
                "city": len([p for p in final_results if p.priority == "city"]),
                "district": len([p for p in final_results if p.priority == "district"]),
                "state": len([p for p in final_results if p.priority == "state"]),
                "language": len([p for p in final_results if p.priority == "language"]),
                "national": len([p for p in final_results if p.priority == "national"])
            }
        }
    }
# =========================================================
# ADVERTISEMENT APIs
# =========================================================

@router.post("/advertisements", response_model=AdvertisementOut, status_code=status.HTTP_201_CREATED)
def create_advertisement(
    ad: AdvertisementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER)),  # Changed from ADMIN to PUBLISHER
):
    """
    Create a new advertisement
    - PUBLISHER: Creates as pending (requires admin approval)
    - ADMIN: Can create as approved (by setting is_approved=True)
    """
    # Validate dates
    if ad.start_date >= ad.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Validate location IDs if provided
    if ad.state_id:
        state = db.query(State).filter(State.id == ad.state_id).first()
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state ID")
    
    if ad.district_id:
        district = db.query(District).filter(District.id == ad.district_id).first()
        if not district:
            raise HTTPException(status_code=400, detail="Invalid district ID")
    
    if ad.city_id:
        city = db.query(City).filter(City.id == ad.city_id).first()
        if not city:
            raise HTTPException(status_code=400, detail="Invalid city ID")
    
    if ad.language_id:
        language = db.query(Language).filter(Language.id == ad.language_id).first()
        if not language:
            raise HTTPException(status_code=400, detail="Invalid language ID")
    
    # Determine approval status based on user role
    is_approved = False
    if current_user.role == UserRole.ADMIN:
        is_approved = True  # Admin creates as approved
    # else: PUBLISHER creates as pending (is_approved = False)
    
    # Create ad data dictionary
    ad_data = {
        "title": ad.title,
        "image_url": ad.image_url,
        "redirect_url": ad.redirect_url,
        "placement": ad.placement,
        "start_date": ad.start_date,
        "end_date": ad.end_date,
        "state_id": ad.state_id,
        "district_id": ad.district_id,
        "city_id": ad.city_id,
        "language_id": ad.language_id,
        "is_active": ad.is_active,
        "is_approved": is_approved,
        "is_premium": ad.is_premium,
        "premium_priority": ad.premium_priority,# ✅ Add approval status
        "created_by": current_user.user_uid,  # Track who created
    }
    
    # Add targeting fields
    if ad.targeting:
        if ad.targeting.gender:
            ad_data["target_gender"] = ad.targeting.gender
        if ad.targeting.age_min:
            ad_data["target_age_min"] = ad.targeting.age_min
        if ad.targeting.age_max:
            ad_data["target_age_max"] = ad.targeting.age_max
        if ad.targeting.languages and not ad.language_id:
            ad_data["language_id"] = ad.targeting.languages[0]
    
    # Create ad
    new_ad = Advertisement(**ad_data)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    
    return new_ad


@router.get("/advertisements", response_model=PaginatedAdvertisementsOut)
def get_all_advertisements(
    # Filters
    is_approved: Optional[bool] = Query(None, description="Filter by approval status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    placement: Optional[str] = Query(None, description="Filter by placement"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    language_id: Optional[int] = Query(None, description="Filter by language"),
    created_by: Optional[str] = Query(None, description="Filter by creator UID"),
    
    # Date filters
    from_date: Optional[datetime] = Query(None, description="Created from date"),
    to_date: Optional[datetime] = Query(None, description="Created to date"),
    start_from: Optional[datetime] = Query(None, description="Campaign start from"),
    start_to: Optional[datetime] = Query(None, description="Campaign start to"),
    end_from: Optional[datetime] = Query(None, description="Campaign end from"),
    end_to: Optional[datetime] = Query(None, description="Campaign end to"),
    
    # Search
    search: Optional[str] = Query(None, min_length=2, description="Search by title"),
    
    # Sorting
    sort_by: str = Query("created_at", enum=["created_at", "start_date", "end_date", "title", "views"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    
    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get all advertisements with advanced filters (Admin only)
    """
    query = db.query(Advertisement)
    
    # Apply filters
    if is_approved is not None:
        query = query.filter(Advertisement.is_approved == is_approved)
    if is_active is not None:
        query = query.filter(Advertisement.is_active == is_active)
    if placement:
        query = query.filter(Advertisement.placement == placement)
    if state_id:
        query = query.filter(Advertisement.state_id == state_id)
    if district_id:
        query = query.filter(Advertisement.district_id == district_id)
    if city_id:
        query = query.filter(Advertisement.city_id == city_id)
    if language_id:
        query = query.filter(Advertisement.language_id == language_id)
    if created_by:
        query = query.filter(Advertisement.created_by == created_by)
    
    # Date range filters
    if from_date:
        query = query.filter(Advertisement.created_at >= from_date)
    if to_date:
        query = query.filter(Advertisement.created_at <= to_date)
    if start_from:
        query = query.filter(Advertisement.start_date >= start_from)
    if start_to:
        query = query.filter(Advertisement.start_date <= start_to)
    if end_from:
        query = query.filter(Advertisement.end_date >= end_from)
    if end_to:
        query = query.filter(Advertisement.end_date <= end_to)
    
    # Search by title
    if search:
        query = query.filter(Advertisement.title.ilike(f"%{search}%"))
    
    # Apply sorting
    sort_column = getattr(Advertisement, sort_by, Advertisement.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return PaginatedAdvertisementsOut(
        total=total,
        page=page,
        limit=limit,
        items=items
    )

@router.put("/advertisements/{ad_id}", response_model=AdvertisementOut)
def update_advertisement(
    ad_id: int,
    ad_update: AdvertisementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update advertisement (Admin only)"""
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Update basic fields
    if ad_update.title is not None:
        ad.title = ad_update.title
    if ad_update.image_url is not None:
        ad.image_url = ad_update.image_url
    if ad_update.redirect_url is not None:
        ad.redirect_url = ad_update.redirect_url
    if ad_update.placement is not None:
        ad.placement = ad_update.placement
    if ad_update.start_date is not None:
        ad.start_date = ad_update.start_date
    if ad_update.end_date is not None:
        ad.end_date = ad_update.end_date
    if ad_update.state_id is not None:
        ad.state_id = ad_update.state_id
    if ad_update.district_id is not None:
        ad.district_id = ad_update.district_id
    if ad_update.city_id is not None:
        ad.city_id = ad_update.city_id
    if ad_update.language_id is not None:
        ad.language_id = ad_update.language_id
    if ad_update.is_active is not None:
        ad.is_active = ad_update.is_active
    
    # Update targeting fields (flatten targeting object)
    if ad_update.targeting:
        if ad_update.targeting.gender is not None:
            ad.target_gender = ad_update.targeting.gender
        if ad_update.targeting.age_min is not None:
            ad.target_age_min = ad_update.targeting.age_min
        if ad_update.targeting.age_max is not None:
            ad.target_age_max = ad_update.targeting.age_max
        if ad_update.targeting.languages and not ad_update.language_id:
            ad.language_id = ad_update.targeting.languages[0]
    
    ad.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ad)
    
    return ad
@router.get("/advertisements/active", response_model=dict)
def get_active_advertisements(
    user_uid: Optional[str] = Query(None),
    placement: str = Query("feed"),
    limit: int = Query(10),
    session_id: Optional[str] = Query(None),
    include_premium: bool = Query(True, description="Include premium ads at top"),
    premium_limit: int = Query(1, ge=0, le=3, description="Number of premium ads to show"),
    exclude_seen: bool = Query(True, description="Exclude ads already seen in this session"),  # ✅ ADD THIS PARAMETER
    db: Session = Depends(get_db),
):
    """
    Get active advertisements with premium ads at top
    """
    current_time = datetime.utcnow()
    
    # Base query: active and approved ads
    query = db.query(Advertisement).filter(
        Advertisement.is_active == True,
        Advertisement.is_approved == True,
        Advertisement.start_date <= current_time,
        Advertisement.end_date >= current_time
    )
    
    if placement:
        query = query.filter(Advertisement.placement == placement)
    
    # Get user preferences
    user_pref = None
    if user_uid:
        user_pref = db.query(UserPreference).filter(
            UserPreference.user_uid == user_uid
        ).first()
        
        # Also get user's location from user table if preferences not set
        if not user_pref:
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if user:
                class TempPref:
                    pass
                user_pref = TempPref()
                user_pref.city_id = user.city_id
                user_pref.district_id = user.district_id
                user_pref.state_id = user.state_id
                user_pref.language_id = None
                user_pref.gender = user.gender
    
    # Track seen ads in this session
    seen_ids = set()
    if exclude_seen and session_id:
        try:
            seen_ads = db.query(AdImpression.ad_id).filter(
                AdImpression.session_id == session_id
            ).all()
            seen_ids = {ad[0] for ad in seen_ads}
        except Exception as e:
            print(f"Error querying AdImpression: {e}")
    
    results = []
    
    # =========================================================
    # PRIORITY 0: PREMIUM ADS (Show at top of feed)
    # =========================================================
    premium_ads = []
    if include_premium:
        premium_query = query.filter(Advertisement.is_premium == True)
        
        # Apply location targeting for premium ads
        if user_pref:
            location_conditions = []
            if user_pref.city_id:
                location_conditions.append(Advertisement.city_id == user_pref.city_id)
            if user_pref.district_id:
                location_conditions.append(Advertisement.district_id == user_pref.district_id)
            if user_pref.state_id:
                location_conditions.append(Advertisement.state_id == user_pref.state_id)
            
            if location_conditions:
                premium_query = premium_query.filter(or_(*location_conditions))
        
        # Sort by premium priority (higher first)
        premium_ads = premium_query.order_by(
            desc(Advertisement.premium_priority),
            desc(Advertisement.created_at)
        ).all()
        
        # Filter out seen ads
        premium_ads = [ad for ad in premium_ads if ad.id not in seen_ids]
        
        # Mark priority
        for ad in premium_ads[:premium_limit]:
            ad.priority = "premium"
            ad.priority_level = 0
            ad.cpm_multiplier = 3.0
            results.append(ad)
            seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 1: CITY ADS (Highest Revenue)
    # =========================================================
    if len(results) < limit and user_pref and user_pref.city_id:
        city_ads = query.filter(
            Advertisement.city_id == user_pref.city_id,
            Advertisement.is_premium == False
        )
        
        if user_pref.language_id:
            city_ads = city_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in city_ads.all():
            if len(results) >= limit:
                break
            if ad.id not in seen_ids:
                ad.priority = "city"
                ad.priority_level = 1
                ad.cpm_multiplier = 2.0
                results.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 2: DISTRICT ADS
    # =========================================================
    if len(results) < limit and user_pref and user_pref.district_id:
        district_ads = query.filter(
            Advertisement.district_id == user_pref.district_id,
            Advertisement.is_premium == False,
            Advertisement.city_id == None
        )
        
        if user_pref.language_id:
            district_ads = district_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in district_ads.all():
            if len(results) >= limit:
                break
            if ad.id not in seen_ids:
                ad.priority = "district"
                ad.priority_level = 2
                ad.cpm_multiplier = 1.5
                results.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 3: STATE ADS
    # =========================================================
    if len(results) < limit and user_pref and user_pref.state_id:
        state_ads = query.filter(
            Advertisement.state_id == user_pref.state_id,
            Advertisement.is_premium == False,
            Advertisement.city_id == None,
            Advertisement.district_id == None
        )
        
        if user_pref.language_id:
            state_ads = state_ads.filter(
                or_(
                    Advertisement.language_id == user_pref.language_id,
                    Advertisement.language_id == None
                )
            )
        
        for ad in state_ads.all():
            if len(results) >= limit:
                break
            if ad.id not in seen_ids:
                ad.priority = "state"
                ad.priority_level = 3
                ad.cpm_multiplier = 1.2
                results.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 4: LANGUAGE ADS
    # =========================================================
    if len(results) < limit and user_pref and user_pref.language_id:
        lang_ads = query.filter(
            Advertisement.language_id == user_pref.language_id,
            Advertisement.is_premium == False,
            Advertisement.state_id == None,
            Advertisement.district_id == None,
            Advertisement.city_id == None
        )
        
        for ad in lang_ads.all():
            if len(results) >= limit:
                break
            if ad.id not in seen_ids:
                ad.priority = "language"
                ad.priority_level = 4
                ad.cpm_multiplier = 1.0
                results.append(ad)
                seen_ids.add(ad.id)
    
    # =========================================================
    # PRIORITY 5: NATIONAL ADS (Fill Inventory)
    # =========================================================
    if len(results) < limit:
        national_ads = query.filter(
            Advertisement.is_premium == False,
            Advertisement.state_id == None,
            Advertisement.district_id == None,
            Advertisement.city_id == None
        )
        
        for ad in national_ads.all():
            if len(results) >= limit:
                break
            if ad.id not in seen_ids:
                ad.priority = "national"
                ad.priority_level = 5
                ad.cpm_multiplier = 0.8
                results.append(ad)
                seen_ids.add(ad.id)
    
    # Sort by priority level (0 = highest)
    results.sort(key=lambda x: x.priority_level)
    
    # Log impressions for analytics
    for ad in results:
        try:
            impression = AdImpression(
                ad_id=ad.id,
                user_uid=user_uid,
                session_id=session_id,
                impression_at=datetime.utcnow()
            )
            db.add(impression)
        except Exception as e:
            print(f"Error logging impression: {e}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing impressions: {e}")
    
    return {
        "ads": results,
        "metadata": {
            "total_available": len(results),
            "returned": len(results),
            "has_premium": len([a for a in results if a.priority == "premium"]) > 0,
            "premium_count": len([a for a in results if a.priority == "premium"]),
            "priority_breakdown": {
                "premium": len([a for a in results if a.priority == "premium"]),
                "city": len([a for a in results if a.priority == "city"]),
                "district": len([a for a in results if a.priority == "district"]),
                "state": len([a for a in results if a.priority == "state"]),
                "language": len([a for a in results if a.priority == "language"]),
                "national": len([a for a in results if a.priority == "national"])
            }
        }
    }
@router.get("/advertisements/{ad_id}", response_model=AdvertisementOut)
def get_advertisement(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get advertisement by ID (Admin only)"""
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

# Then add approval endpoint
@router.put("/advertisements/{ad_id}/moderate", response_model=dict)
def moderate_advertisement(
    ad_id: int,
    action: str = Query(..., enum=["approve", "reject"], description="Action to perform"),
    reason: Optional[str] = Query(None, description="Rejection reason (required for reject)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Moderate an advertisement - approve or reject (Admin only)
    
    - **action**: 'approve' to approve, 'reject' to reject
    - **reason**: Required for rejection
    """
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    if action == "approve":
        if ad.is_approved:
            raise HTTPException(status_code=400, detail="Advertisement already approved")
        
        ad.is_approved = True
        ad.is_active = True
        ad.approved_at = datetime.utcnow()
        ad.approved_by = current_user.user_uid
        ad.rejected_at = None
        ad.rejected_by = None
        ad.rejection_reason = None
        
        message = f"Advertisement {ad_id} approved successfully"
        
    elif action == "reject":
        if ad.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved advertisement")
        
        if not reason:
            raise HTTPException(status_code=400, detail="Rejection reason is required")
        
        ad.is_approved = False
        ad.is_active = False
        ad.rejected_at = datetime.utcnow()
        ad.rejected_by = current_user.user_uid
        ad.rejection_reason = reason
        ad.approved_at = None
        ad.approved_by = None
        
        message = f"Advertisement {ad_id} rejected"
    
    ad.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ad)
    
    return {
        "message": message,
        "ad_id": ad_id,
        "action": action,
        "ad": ad
    }



@router.delete("/advertisements/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advertisement(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete advertisement (Admin only)"""
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    db.delete(ad)
    db.commit()
    return None


@router.post("/advertisements/{ad_id}/toggle-status", response_model=dict)
def toggle_ad_status(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Toggle advertisement active status (Admin only)"""
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    ad.is_active = not ad.is_active
    ad.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"Ad {ad_id} {'activated' if ad.is_active else 'deactivated'}"}

@router.put("/content/{content_type}/{content_id}/moderate", response_model=dict)
def moderate_content(
    content_type: str,  # This is a PATH parameter - no Query() wrapper
    content_id: int,    # This is a PATH parameter - no Query() wrapper
    action: str = Query(..., enum=["approve", "reject"], description="Action to perform"),
    reason: Optional[str] = Query(None, description="Rejection reason (required for reject)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Moderate any content type - approve or reject (Admin only)
    
    - **content_type**: 'advertisement' or 'sponsored_post' (path parameter)
    - **content_id**: ID of the content (path parameter)
    - **action**: 'approve' or 'reject' (query parameter)
    - **reason**: Required for rejection (query parameter)
    """
    
    if content_type == "advertisement":
        content = db.query(Advertisement).filter(Advertisement.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Advertisement not found")
        
        if action == "approve":
            if content.is_approved:
                raise HTTPException(status_code=400, detail="Already approved")
            
            content.is_approved = True
            content.is_active = True
            content.approved_at = datetime.utcnow()
            content.approved_by = current_user.user_uid
            content.rejected_at = None
            content.rejected_by = None
            content.rejection_reason = None
            
        elif action == "reject":
            if content.is_approved:
                raise HTTPException(status_code=400, detail="Cannot reject already approved content")
            
            if not reason:
                raise HTTPException(status_code=400, detail="Rejection reason is required")
            
            content.is_approved = False
            content.is_active = False
            content.rejected_at = datetime.utcnow()
            content.rejected_by = current_user.user_uid
            content.rejection_reason = reason
            content.approved_at = None
            content.approved_by = None
        
        content.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(content)
        
        return {
            "message": f"Advertisement {content_id} {action}ed successfully",
            "content_type": content_type,
            "content_id": content_id,
            "action": action,
            "content": content
        }
    
    elif content_type == "sponsored_post":
        content = db.query(SponsoredPost).filter(SponsoredPost.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Sponsored post not found")
        
        if action == "approve":
            if content.is_approved:
                raise HTTPException(status_code=400, detail="Already approved")
            
            content.is_approved = True
            content.approved_at = datetime.utcnow()
            content.approved_by = current_user.user_uid
            content.rejected_at = None
            content.rejected_by = None
            content.rejection_reason = None
            
        elif action == "reject":
            if content.is_approved:
                raise HTTPException(status_code=400, detail="Cannot reject already approved content")
            
            if not reason:
                raise HTTPException(status_code=400, detail="Rejection reason is required")
            
            content.is_approved = False
            content.rejected_at = datetime.utcnow()
            content.rejected_by = current_user.user_uid
            content.rejection_reason = reason
            content.approved_at = None
            content.approved_by = None
        
        content.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(content)
        
        return {
            "message": f"Sponsored Post {content_id} {action}ed successfully",
            "content_type": content_type,
            "content_id": content_id,
            "action": action,
            "content": content
        }
    
    raise HTTPException(status_code=400, detail="Invalid content type. Use 'advertisement' or 'sponsored_post'")

@router.get("/advertisements/pending", response_model=List[AdvertisementOut])
def get_pending_advertisements(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get all pending advertisements (not approved and not rejected)"""
    return db.query(Advertisement)\
        .filter(
            Advertisement.is_approved == False,
            Advertisement.rejected_at == None
        )\
        .order_by(desc(Advertisement.created_at))\
        .offset(offset)\
        .limit(limit)\
        .all()


@router.get("/sponsored-posts/pending", response_model=List[SponsoredPostOut])
def get_pending_sponsored_posts(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get all pending sponsored posts (not approved and not rejected)"""
    return db.query(SponsoredPost)\
        .filter(
            SponsoredPost.is_approved == False,
            SponsoredPost.rejected_at == None
        )\
        .order_by(desc(SponsoredPost.created_at))\
        .offset(offset)\
        .limit(limit)\
        .all()
# =========================================================
# SPONSORED POST APIs
# =========================================================

@router.post("/sponsored-posts", response_model=SponsoredPostOut, status_code=status.HTTP_201_CREATED)
def create_sponsored_post(
    post: SponsoredPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER)),  # Changed from ADMIN to PUBLISHER
):
    """
    Create a new sponsored post
    - PUBLISHER: Creates as pending (requires admin approval)
    - ADMIN: Creates as approved
    """
    try:
        if post.start_date >= post.end_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Validate location IDs
        if post.state_id:
            state = db.query(State).filter(State.id == post.state_id).first()
            if not state:
                raise HTTPException(status_code=400, detail="Invalid state ID")
        
        if post.district_id:
            district = db.query(District).filter(District.id == post.district_id).first()
            if not district:
                raise HTTPException(status_code=400, detail="Invalid district ID")
        
        if post.city_id:
            city = db.query(City).filter(City.id == post.city_id).first()
            if not city:
                raise HTTPException(status_code=400, detail="Invalid city ID")
        
        if post.language_id:
            language = db.query(Language).filter(Language.id == post.language_id).first()
            if not language:
                raise HTTPException(status_code=400, detail="Invalid language ID")
        
        # Determine approval status based on user role
        is_approved = False
        if current_user.role == UserRole.ADMIN:
            is_approved = True  # Admin creates as approved
        
        post_data = {
            "title": post.title,
            "content": post.content,
            "image_url": post.image_url,
            "cta_text": post.cta_text,
            "cta_url": post.cta_url,
            "start_date": post.start_date,
            "end_date": post.end_date,
            "state_id": post.state_id,
            "district_id": post.district_id,
            "city_id": post.city_id,
            "language_id": post.language_id,
            "is_approved": is_approved,  # ✅ Set based on role
            "created_by": current_user.user_uid,  # Track who created
        }
        
        if post.targeting:
            if post.targeting.gender:
                post_data["target_gender"] = post.targeting.gender
            if post.targeting.age_min:
                post_data["target_age_min"] = post.targeting.age_min
            if post.targeting.age_max:
                post_data["target_age_max"] = post.targeting.age_max
        
        new_post = SponsoredPost(**post_data)
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return new_post
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating sponsored post: {str(e)}")
# =========================================================
# SPONSORED POSTS ACTIVE API
# =========================================================

@router.get("/sponsored-posts/active", response_model=dict)
def get_active_sponsored_posts(
    user_uid: Optional[str] = Query(None, description="User for personalized targeting"),
    limit: int = Query(10, ge=1, le=50, description="Maximum posts to return"),
    session_id: Optional[str] = Query(None, description="Session ID for rotation tracking"),
    exclude_seen: bool = Query(True, description="Exclude posts already seen in this session"),
    db: Session = Depends(get_db),
):
    """
    Get active sponsored posts with:
    - Location-based targeting (City > District > State > Language > National)
    - Session-based deduplication
    - Priority-based ordering
    - Impression tracking for analytics
    """
    current_time = datetime.utcnow()
    
    # Base query: active and approved sponsored posts
    query = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= current_time,
        SponsoredPost.end_date >= current_time
    )
    
    # Get user preferences for targeting
    user_pref = None
    if user_uid:
        user_pref = db.query(UserPreference).filter(
            UserPreference.user_uid == user_uid
        ).first()
        
        # Also get user's location from user table if preferences not set
        if not user_pref:
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if user:
                # Create temporary preference object
                class TempPref:
                    pass
                user_pref = TempPref()
                user_pref.city_id = user.city_id
                user_pref.district_id = user.district_id
                user_pref.state_id = user.state_id
                user_pref.language_id = None
                user_pref.gender = user.gender
    
    # Track seen posts in this session
    seen_ids = set()
    if exclude_seen and session_id:
        try:
            seen_posts = db.query(SponsoredImpression.post_id).filter(
                SponsoredImpression.session_id == session_id
            ).all()
            seen_ids = {post[0] for post in seen_posts}
        except Exception as e:
            print(f"Error querying SponsoredImpression: {e}")
    
    all_posts = []
    
    # =========================================================
    # PRIORITY 1: CITY TARGETING (Highest Relevance)
    # =========================================================
    if user_pref and user_pref.city_id:
        city_posts = query.filter(SponsoredPost.city_id == user_pref.city_id)
        
        # Language preference for city posts
        if user_pref.language_id:
            city_posts = city_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in city_posts.all():
            if post.id not in seen_ids:
                post.priority = "city"
                post.priority_level = 1
                post.relevance_score = calculate_sponsored_score(post, user_pref)
                all_posts.append(post)
                seen_ids.add(post.id)
    
    # =========================================================
    # PRIORITY 2: DISTRICT TARGETING
    # =========================================================
    if len(all_posts) < limit and user_pref and user_pref.district_id:
        district_posts = query.filter(
            SponsoredPost.district_id == user_pref.district_id,
            SponsoredPost.city_id == None  # Exclude city posts already handled
        )
        
        if user_pref.language_id:
            district_posts = district_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in district_posts.all():
            if post.id not in seen_ids:
                post.priority = "district"
                post.priority_level = 2
                post.relevance_score = calculate_sponsored_score(post, user_pref)
                all_posts.append(post)
                seen_ids.add(post.id)
    
    # =========================================================
    # PRIORITY 3: STATE TARGETING
    # =========================================================
    if len(all_posts) < limit and user_pref and user_pref.state_id:
        state_posts = query.filter(
            SponsoredPost.state_id == user_pref.state_id,
            SponsoredPost.city_id == None,
            SponsoredPost.district_id == None
        )
        
        if user_pref.language_id:
            state_posts = state_posts.filter(
                or_(
                    SponsoredPost.language_id == user_pref.language_id,
                    SponsoredPost.language_id == None
                )
            )
        
        for post in state_posts.all():
            if post.id not in seen_ids:
                post.priority = "state"
                post.priority_level = 3
                post.relevance_score = calculate_sponsored_score(post, user_pref)
                all_posts.append(post)
                seen_ids.add(post.id)
    
    # =========================================================
    # PRIORITY 4: LANGUAGE TARGETING
    # =========================================================
    if len(all_posts) < limit and user_pref and user_pref.language_id:
        lang_posts = query.filter(
            SponsoredPost.language_id == user_pref.language_id,
            SponsoredPost.state_id == None,
            SponsoredPost.district_id == None,
            SponsoredPost.city_id == None
        )
        
        for post in lang_posts.all():
            if post.id not in seen_ids:
                post.priority = "language"
                post.priority_level = 4
                post.relevance_score = calculate_sponsored_score(post, user_pref)
                all_posts.append(post)
                seen_ids.add(post.id)
    
    # =========================================================
    # PRIORITY 5: NATIONAL POSTS (Fallback)
    # =========================================================
    if len(all_posts) < limit:
        national_posts = query.filter(
            SponsoredPost.state_id == None,
            SponsoredPost.district_id == None,
            SponsoredPost.city_id == None
        )
        
        for post in national_posts.all():
            if post.id not in seen_ids:
                post.priority = "national"
                post.priority_level = 5
                post.relevance_score = calculate_sponsored_score(post, user_pref)
                all_posts.append(post)
                seen_ids.add(post.id)
    
    # =========================================================
    # SORT BY PRIORITY (Higher priority first)
    # =========================================================
    all_posts.sort(key=lambda x: x.priority_level)
    final_posts = all_posts[:limit]
    
    # =========================================================
    # LOG IMPRESSIONS FOR ANALYTICS
    # =========================================================
    for post in final_posts:
        try:
            impression = SponsoredImpression(
                post_id=post.id,
                user_uid=user_uid,
                session_id=session_id,
                impression_at=datetime.utcnow()
            )
            db.add(impression)
        except Exception as e:
            print(f"Error logging sponsored impression: {e}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing impressions: {e}")
    
    return {
        "posts": final_posts,
        "metadata": {
            "total_available": len(all_posts),
            "returned": len(final_posts),
            "priority_breakdown": {
                "city": len([p for p in final_posts if getattr(p, 'priority', None) == "city"]),
                "district": len([p for p in final_posts if getattr(p, 'priority', None) == "district"]),
                "state": len([p for p in final_posts if getattr(p, 'priority', None) == "state"]),
                "language": len([p for p in final_posts if getattr(p, 'priority', None) == "language"]),
                "national": len([p for p in final_posts if getattr(p, 'priority', None) == "national"])
            },
            "session_id": session_id,
            "user_uid": user_uid
        }
    }


def calculate_sponsored_score(post, user_pref):
    """
    Calculate relevance score for sponsored post based on user preferences
    """
    score = 0
    
    if user_pref:
        # Location match (higher weight for closer location)
        if post.city_id and user_pref.city_id and post.city_id == user_pref.city_id:
            score += 100
        elif post.district_id and user_pref.district_id and post.district_id == user_pref.district_id:
            score += 50
        elif post.state_id and user_pref.state_id and post.state_id == user_pref.state_id:
            score += 25
        
        # Language match
        if post.language_id and user_pref.language_id and post.language_id == user_pref.language_id:
            score += 40
        
        # Gender match
        if post.target_gender and user_pref.gender and post.target_gender == user_pref.gender:
            score += 20
    
    return score
   
@router.get("/sponsored-posts", response_model=PaginatedSponsoredPostsOut)
def get_all_sponsored_posts(
    # Filters
    is_approved: Optional[bool] = Query(None, description="Filter by approval status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    language_id: Optional[int] = Query(None, description="Filter by language"),
    created_by: Optional[str] = Query(None, description="Filter by creator UID"),
    
    # Date filters
    from_date: Optional[datetime] = Query(None, description="Created from date"),
    to_date: Optional[datetime] = Query(None, description="Created to date"),
    start_from: Optional[datetime] = Query(None, description="Campaign start from"),
    start_to: Optional[datetime] = Query(None, description="Campaign start to"),
    end_from: Optional[datetime] = Query(None, description="Campaign end from"),
    end_to: Optional[datetime] = Query(None, description="Campaign end to"),
    
    # Search
    search: Optional[str] = Query(None, min_length=2, description="Search by title or content"),
    
    # Sorting
    sort_by: str = Query("created_at", enum=["created_at", "start_date", "end_date", "title"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    
    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get all sponsored posts with advanced filters (Admin only)
    """
    query = db.query(SponsoredPost)
    
    # Apply filters
    if is_approved is not None:
        query = query.filter(SponsoredPost.is_approved == is_approved)
    if state_id:
        query = query.filter(SponsoredPost.state_id == state_id)
    if district_id:
        query = query.filter(SponsoredPost.district_id == district_id)
    if city_id:
        query = query.filter(SponsoredPost.city_id == city_id)
    if language_id:
        query = query.filter(SponsoredPost.language_id == language_id)
    if created_by:
        query = query.filter(SponsoredPost.created_by == created_by)
    
    # Date range filters
    if from_date:
        query = query.filter(SponsoredPost.created_at >= from_date)
    if to_date:
        query = query.filter(SponsoredPost.created_at <= to_date)
    if start_from:
        query = query.filter(SponsoredPost.start_date >= start_from)
    if start_to:
        query = query.filter(SponsoredPost.start_date <= start_to)
    if end_from:
        query = query.filter(SponsoredPost.end_date >= end_from)
    if end_to:
        query = query.filter(SponsoredPost.end_date <= end_to)
    
    # Search by title or content
    if search:
        query = query.filter(
            or_(
                SponsoredPost.title.ilike(f"%{search}%"),
                SponsoredPost.content.ilike(f"%{search}%")
            )
        )
    
    # Apply sorting
    sort_column = getattr(SponsoredPost, sort_by, SponsoredPost.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return PaginatedSponsoredPostsOut(
        total=total,
        page=page,
        limit=limit,
        items=items
    )

@router.get("/statistics", tags=["Admin"])
def get_ads_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get comprehensive ad and sponsored post statistics (Admin only)
    """
    current_time = datetime.utcnow()
    
    # Advertisement stats
    total_ads = db.query(Advertisement).count()
    pending_ads = db.query(Advertisement).filter(
        Advertisement.is_approved == False,
        Advertisement.rejected_at == None
    ).count()
    approved_ads = db.query(Advertisement).filter(Advertisement.is_approved == True).count()
    rejected_ads = db.query(Advertisement).filter(Advertisement.rejected_at != None).count()
    active_ads = db.query(Advertisement).filter(
        Advertisement.is_approved == True,
        Advertisement.is_active == True,
        Advertisement.start_date <= current_time,
        Advertisement.end_date >= current_time
    ).count()
    expired_ads = db.query(Advertisement).filter(
        Advertisement.is_approved == True,
        Advertisement.end_date < current_time
    ).count()
    upcoming_ads = db.query(Advertisement).filter(
        Advertisement.is_approved == True,
        Advertisement.start_date > current_time
    ).count()
    
    # Sponsored post stats
    total_posts = db.query(SponsoredPost).count()
    pending_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == False,
        SponsoredPost.rejected_at == None
    ).count()
    approved_posts = db.query(SponsoredPost).filter(SponsoredPost.is_approved == True).count()
    rejected_posts = db.query(SponsoredPost).filter(SponsoredPost.rejected_at != None).count()
    active_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= current_time,
        SponsoredPost.end_date >= current_time
    ).count()
    expired_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.end_date < current_time
    ).count()
    
    # Location distribution
    location_stats = db.query(
        State.name,
        func.count(Advertisement.id).label('ad_count')
    ).join(State, Advertisement.state_id == State.id).group_by(State.name).all()
    
    # Language distribution
    language_stats = db.query(
        Language.name,
        func.count(Advertisement.id).label('ad_count')
    ).join(Language, Advertisement.language_id == Language.id).group_by(Language.name).all()
    
    return {
        "advertisements": {
            "total": total_ads,
            "pending": pending_ads,
            "approved": approved_ads,
            "rejected": rejected_ads,
            "active": active_ads,
            "expired": expired_ads,
            "upcoming": upcoming_ads,
            "approval_rate": round(approved_ads / total_ads * 100, 2) if total_ads > 0 else 0
        },
        "sponsored_posts": {
            "total": total_posts,
            "pending": pending_posts,
            "approved": approved_posts,
            "rejected": rejected_posts,
            "active": active_posts,
            "expired": expired_posts,
            "approval_rate": round(approved_posts / total_posts * 100, 2) if total_posts > 0 else 0
        },
        "distribution": {
            "by_state": [{"state": s.name, "ad_count": s.ad_count} for s in location_stats],
            "by_language": [{"language": l.name, "ad_count": l.ad_count} for l in language_stats]
        }
    }


@router.put("/sponsored-posts/{post_id}", response_model=SponsoredPostOut)
def update_sponsored_post(
    post_id: int,
    post_update: SponsoredPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update sponsored post (Admin only)"""
    try:
        # Get existing post
        post = db.query(SponsoredPost).filter(SponsoredPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Sponsored post not found")
        
        # Validate dates if provided
        if post_update.start_date and post_update.end_date:
            if post_update.start_date >= post_update.end_date:
                raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Validate location IDs if provided
        if hasattr(post_update, 'state_id') and post_update.state_id:
            state = db.query(State).filter(State.id == post_update.state_id).first()
            if not state:
                raise HTTPException(status_code=400, detail="Invalid state ID")
        
        if hasattr(post_update, 'district_id') and post_update.district_id:
            district = db.query(District).filter(District.id == post_update.district_id).first()
            if not district:
                raise HTTPException(status_code=400, detail="Invalid district ID")
        
        if hasattr(post_update, 'city_id') and post_update.city_id:
            city = db.query(City).filter(City.id == post_update.city_id).first()
            if not city:
                raise HTTPException(status_code=400, detail="Invalid city ID")
        
        if post_update.language_id:
            language = db.query(Language).filter(Language.id == post_update.language_id).first()
            if not language:
                raise HTTPException(status_code=400, detail="Invalid language ID")
        
        # Update fields
        if post_update.title is not None:
            post.title = post_update.title
        if post_update.content is not None:
            post.content = post_update.content
        if post_update.image_url is not None:
            post.image_url = post_update.image_url
        if post_update.cta_text is not None:
            post.cta_text = post_update.cta_text
        if post_update.cta_url is not None:
            post.cta_url = post_update.cta_url
        if post_update.start_date is not None:
            post.start_date = post_update.start_date
        if post_update.end_date is not None:
            post.end_date = post_update.end_date
        if hasattr(post_update, 'state_id') and post_update.state_id is not None:
            post.state_id = post_update.state_id
        if hasattr(post_update, 'district_id') and post_update.district_id is not None:
            post.district_id = post_update.district_id
        if hasattr(post_update, 'city_id') and post_update.city_id is not None:
            post.city_id = post_update.city_id
        if post_update.language_id is not None:
            post.language_id = post_update.language_id
        
        # Update targeting fields
        if post_update.targeting:
            if post_update.targeting.gender is not None:
                post.target_gender = post_update.targeting.gender
            if post_update.targeting.age_min is not None:
                post.target_age_min = post_update.targeting.age_min
            if post_update.targeting.age_max is not None:
                post.target_age_max = post_update.targeting.age_max
        
        post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating sponsored post: {str(e)}")
    
@router.put("/sponsored-posts/{post_id}/moderate", response_model=dict)
def moderate_sponsored_post(
    post_id: int,
    action: str = Query(..., enum=["approve", "reject"], description="Action to perform"),
    reason: Optional[str] = Query(None, description="Rejection reason (required for reject)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Moderate a sponsored post - approve or reject (Admin only)
    
    - **action**: 'approve' to approve, 'reject' to reject
    - **reason**: Required for rejection
    """
    post = db.query(SponsoredPost).filter(SponsoredPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Sponsored post not found")
    
    if action == "approve":
        if post.is_approved:
            raise HTTPException(status_code=400, detail="Sponsored post already approved")
        
        post.is_approved = True
        post.approved_at = datetime.utcnow()
        post.approved_by = current_user.user_uid
        post.rejected_at = None
        post.rejected_by = None
        post.rejection_reason = None
        
        message = f"Sponsored post {post_id} approved successfully"
        
    elif action == "reject":
        if post.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved sponsored post")
        
        if not reason:
            raise HTTPException(status_code=400, detail="Rejection reason is required")
        
        post.is_approved = False
        post.rejected_at = datetime.utcnow()
        post.rejected_by = current_user.user_uid
        post.rejection_reason = reason
        post.approved_at = None
        post.approved_by = None
        
        message = f"Sponsored post {post_id} rejected"
    
    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    
    return {
        "message": message,
        "post_id": post_id,
        "action": action,
        "post": post
    }
@router.delete("/sponsored-posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sponsored_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete sponsored post (Admin only)"""
    post = db.query(SponsoredPost).filter(SponsoredPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Sponsored post not found")
    
    db.delete(post)
    db.commit()
    return None


# =========================================================
# ANALYTICS & STATISTICS
# =========================================================

@router.get("/ads/statistics", tags=["Admin"])
def get_ads_statistics_detailed(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get comprehensive ad statistics (Admin only)
    """
    current_time = datetime.utcnow()
    
    # Advertisement stats
    total_ads = db.query(Advertisement).count()
    active_ads = db.query(Advertisement).filter(
        Advertisement.is_active == True,
        Advertisement.start_date <= current_time,
        Advertisement.end_date >= current_time
    ).count()
    expired_ads = db.query(Advertisement).filter(
        Advertisement.end_date < current_time
    ).count()
    upcoming_ads = db.query(Advertisement).filter(
        Advertisement.start_date > current_time
    ).count()
    
    # Sponsored post stats
    total_posts = db.query(SponsoredPost).count()
    approved_posts = db.query(SponsoredPost).filter(SponsoredPost.is_approved == True).count()
    pending_posts = db.query(SponsoredPost).filter(SponsoredPost.is_approved == False).count()
    active_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= current_time,
        SponsoredPost.end_date >= current_time
    ).count()
    
    # Location distribution
    location_stats = db.query(
        State.name,
        func.count(Advertisement.id).label('ad_count')
    ).join(State, Advertisement.state_id == State.id).group_by(State.name).all()
    
    # Language distribution
    language_stats = db.query(
        Language.name,
        func.count(Advertisement.id).label('ad_count')
    ).join(Language, Advertisement.language_id == Language.id).group_by(Language.name).all()
    
    return {
        "advertisements": {
            "total": total_ads,
            "active": active_ads,
            "expired": expired_ads,
            "upcoming": upcoming_ads
        },
        "sponsored_posts": {
            "total": total_posts,
            "approved": approved_posts,
            "pending": pending_posts,
            "active": active_posts
        },
        "distribution": {
            "by_state": [{"state": s.name, "count": s.ad_count} for s in location_stats],
            "by_language": [{"language": l.name, "count": l.ad_count} for l in language_stats]
        }
    }


@router.get("/targeting-options", tags=["Admin"])
def get_targeting_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get available targeting options for ads
    """
    languages = db.query(Language).all()
    states = db.query(State).all()
    
    # Get districts per state
    states_with_districts = []
    for state in states:
        districts = db.query(District).filter(District.state_id == state.id).all()
        states_with_districts.append({
            "id": state.id,
            "name": state.name,
            "districts": [{"id": d.id, "name": d.name} for d in districts]
        })
    
    return {
        "languages": [{"id": l.id, "name": l.name, "code": l.code} for l in languages],
        "states": states_with_districts,
        "genders": ["male", "female", "all"],
        "age_ranges": ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    }
    
@router.get("/overview", response_model=dict)
def get_admin_dashboard_overview(
    period: str = Query("week", enum=["day", "week", "month", "year"], description="Time period for analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get comprehensive admin dashboard overview with all content types.
    """
    current_time = datetime.utcnow()
    
    # Define time ranges
    if period == "day":
        start_date = current_time - timedelta(days=1)
    elif period == "week":
        start_date = current_time - timedelta(days=7)
    elif period == "month":
        start_date = current_time - timedelta(days=30)
    else:  # year
        start_date = current_time - timedelta(days=365)
    
    # =========================================================
    # 1. ADVERTISEMENTS STATISTICS
    # =========================================================
    
    ads_total = db.query(Advertisement).count()
    ads_pending = db.query(Advertisement).filter(
        Advertisement.is_approved == False,
        Advertisement.rejected_at == None
    ).count()
    ads_approved = db.query(Advertisement).filter(Advertisement.is_approved == True).count()
    ads_rejected = db.query(Advertisement).filter(Advertisement.rejected_at != None).count()
    ads_active = db.query(Advertisement).filter(
        Advertisement.is_approved == True,
        Advertisement.is_active == True,
        Advertisement.start_date <= current_time,
        Advertisement.end_date >= current_time
    ).count()
    ads_expired = db.query(Advertisement).filter(
        Advertisement.end_date < current_time
    ).count()
    ads_upcoming = db.query(Advertisement).filter(
        Advertisement.start_date > current_time
    ).count()
    
    # New ads in period
    ads_new = db.query(Advertisement).filter(
        Advertisement.created_at >= start_date
    ).count()
    
    # Ads by placement
    ads_by_placement = db.query(
        Advertisement.placement,
        func.count(Advertisement.id).label('count')
    ).group_by(Advertisement.placement).all()
    
    # Ads by state
    ads_by_state = db.query(
        State.name,
        func.count(Advertisement.id).label('count')
    ).join(State, Advertisement.state_id == State.id).group_by(State.name).limit(10).all()
    
    # =========================================================
    # 2. SPONSORED POSTS STATISTICS
    # =========================================================
    
    posts_total = db.query(SponsoredPost).count()
    posts_pending = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == False,
        SponsoredPost.rejected_at == None
    ).count()
    posts_approved = db.query(SponsoredPost).filter(SponsoredPost.is_approved == True).count()
    posts_rejected = db.query(SponsoredPost).filter(SponsoredPost.rejected_at != None).count()
    posts_active = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= current_time,
        SponsoredPost.end_date >= current_time
    ).count()
    posts_expired = db.query(SponsoredPost).filter(
        SponsoredPost.end_date < current_time
    ).count()
    posts_upcoming = db.query(SponsoredPost).filter(
        SponsoredPost.start_date > current_time
    ).count()
    
    # New posts in period
    posts_new = db.query(SponsoredPost).filter(
        SponsoredPost.created_at >= start_date
    ).count()
    
    # =========================================================
    # 3. EVENTS STATISTICS
    # =========================================================
    
    events_total = db.query(Event).count()
    events_pending = db.query(Event).filter(
        Event.is_approved == False
    ).count()
    events_approved = db.query(Event).filter(Event.is_approved == True).count()
    events_upcoming = db.query(Event).filter(
        Event.is_approved == True,
        Event.event_date >= current_time.date()
    ).count()
    events_today = db.query(Event).filter(
        Event.is_approved == True,
        func.date(Event.event_date) == current_time.date()
    ).count()
    events_past = db.query(Event).filter(
        Event.event_date < current_time.date()
    ).count()
    
    # New events in period
    events_new = db.query(Event).filter(
        Event.created_at >= start_date
    ).count()
    
    # Events by location
    events_by_state = db.query(
        State.name,
        func.count(Event.id).label('count')
    ).join(State, Event.state_id == State.id).group_by(State.name).limit(10).all()
    
    # Online vs Offline events
    events_online = db.query(Event).filter(Event.is_online == True).count()
    events_offline = db.query(Event).filter(Event.is_online == False).count()
    
    # =========================================================
    # 4. POLLS STATISTICS
    # =========================================================
    
    polls_total = db.query(Poll).count()
    polls_pending = db.query(Poll).filter(
        Poll.is_approved == False
    ).count()
    polls_approved = db.query(Poll).filter(Poll.is_approved == True).count()
    polls_active = db.query(Poll).filter(
        Poll.is_approved == True,
        (Poll.expires_at == None) | (Poll.expires_at > current_time)
    ).count()
    polls_expired = db.query(Poll).filter(
        Poll.expires_at != None,
        Poll.expires_at <= current_time
    ).count()
    
    # New polls in period
    polls_new = db.query(Poll).filter(
        Poll.created_at >= start_date
    ).count()
    
    # Total votes across all polls
    total_votes = db.query(func.sum(func.array_length(Poll.votes, 1))).scalar() or 0
    
    # =========================================================
    # 5. TIME SERIES DATA (Last 30 days)
    # =========================================================
    
    thirty_days_ago = current_time - timedelta(days=30)
    
    daily_stats = []
    for i in range(30):
        day_start = (current_time - timedelta(days=29-i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_stats = {
            "date": day_start.date().isoformat(),
            "ads_created": db.query(Advertisement).filter(
                Advertisement.created_at >= day_start,
                Advertisement.created_at < day_end
            ).count(),
            "posts_created": db.query(SponsoredPost).filter(
                SponsoredPost.created_at >= day_start,
                SponsoredPost.created_at < day_end
            ).count(),
            "events_created": db.query(Event).filter(
                Event.created_at >= day_start,
                Event.created_at < day_end
            ).count(),
            "polls_created": db.query(Poll).filter(
                Poll.created_at >= day_start,
                Poll.created_at < day_end
            ).count(),
        }
        daily_stats.append(day_stats)
    
    # =========================================================
    # 6. TOP PERFORMING CONTENT
    # =========================================================
    
    # Top ads by title (based on created date - you can add click tracking)
    top_ads = db.query(Advertisement).filter(
        Advertisement.is_approved == True
    ).order_by(desc(Advertisement.created_at)).limit(5).all()
    
    # Top sponsored posts
    top_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True
    ).order_by(desc(SponsoredPost.created_at)).limit(5).all()
    
    # Upcoming events
    upcoming_events = db.query(Event).filter(
        Event.is_approved == True,
        Event.event_date >= current_time.date()
    ).order_by(Event.event_date.asc()).limit(5).all()
    
    # Active polls
    active_polls = db.query(Poll).filter(
        Poll.is_approved == True,
        (Poll.expires_at == None) | (Poll.expires_at > current_time)
    ).order_by(desc(Poll.created_at)).limit(5).all()
    
    # =========================================================
    # 7. RESPONSE
    # =========================================================
    
    return {
        "period": period,
        "period_start": start_date.isoformat(),
        "period_end": current_time.isoformat(),
        
        "advertisements": {
            "total": ads_total,
            "pending": ads_pending,
            "approved": ads_approved,
            "rejected": ads_rejected,
            "active": ads_active,
            "expired": ads_expired,
            "upcoming": ads_upcoming,
            "new_in_period": ads_new,
            "approval_rate": round(ads_approved / ads_total * 100, 2) if ads_total > 0 else 0,
            "by_placement": [{"placement": p.placement, "count": p.count} for p in ads_by_placement],
            "by_state": [{"state": s.name, "count": s.count} for s in ads_by_state]
        },
        
        "sponsored_posts": {
            "total": posts_total,
            "pending": posts_pending,
            "approved": posts_approved,
            "rejected": posts_rejected,
            "active": posts_active,
            "expired": posts_expired,
            "upcoming": posts_upcoming,
            "new_in_period": posts_new,
            "approval_rate": round(posts_approved / posts_total * 100, 2) if posts_total > 0 else 0
        },
        
        "events": {
            "total": events_total,
            "pending": events_pending,
            "approved": events_approved,
            "upcoming": events_upcoming,
            "today": events_today,
            "past": events_past,
            "new_in_period": events_new,
            "online": events_online,
            "offline": events_offline,
            "by_state": [{"state": s.name, "count": s.count} for s in events_by_state]
        },
        
        "polls": {
            "total": polls_total,
            "pending": polls_pending,
            "approved": polls_approved,
            "active": polls_active,
            "expired": polls_expired,
            "new_in_period": polls_new,
            "total_votes": total_votes,
            "approval_rate": round(polls_approved / polls_total * 100, 2) if polls_total > 0 else 0
        },
        
        "daily_trends": daily_stats,
        
        "top_content": {
            "advertisements": [
                {"id": ad.id, "title": ad.title, "created_at": ad.created_at}
                for ad in top_ads
            ],
            "sponsored_posts": [
                {"id": p.id, "title": p.title, "created_at": p.created_at}
                for p in top_posts
            ],
            "upcoming_events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "event_date": e.event_date,
                    "location": e.location
                }
                for e in upcoming_events
            ],
            "active_polls": [
                {
                    "id": p.id,
                    "question": p.question,
                    "total_votes": sum(p.votes) if p.votes else 0,
                    "expires_at": p.expires_at
                }
                for p in active_polls
            ]
        }
    }


# =========================================================
# DETAILED ANALYTICS APIS
# =========================================================

@router.get("/advertisements/analytics", response_model=dict)
def get_advertisements_analytics(
    period: str = Query("month", enum=["week", "month", "year"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get detailed advertisements analytics
    """
    current_time = datetime.utcnow()
    
    if period == "week":
        start_date = current_time - timedelta(days=7)
    elif period == "month":
        start_date = current_time - timedelta(days=30)
    else:  # year
        start_date = current_time - timedelta(days=365)
    
    # Daily breakdown
    daily_breakdown = []
    days = (current_time - start_date).days
    
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        daily_breakdown.append({
            "date": day_start.date().isoformat(),
            "created": db.query(Advertisement).filter(
                Advertisement.created_at >= day_start,
                Advertisement.created_at < day_end
            ).count(),
            "approved": db.query(Advertisement).filter(
                Advertisement.approved_at >= day_start,
                Advertisement.approved_at < day_end
            ).count(),
            "rejected": db.query(Advertisement).filter(
                Advertisement.rejected_at >= day_start,
                Advertisement.rejected_at < day_end
            ).count()
        })
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": current_time.isoformat(),
        "daily_breakdown": daily_breakdown,
        "summary": {
            "total_created": db.query(Advertisement).filter(Advertisement.created_at >= start_date).count(),
            "total_approved": db.query(Advertisement).filter(Advertisement.approved_at >= start_date).count(),
            "total_rejected": db.query(Advertisement).filter(Advertisement.rejected_at >= start_date).count()
        }
    }


@router.get("/sponsored-posts/analytics", response_model=dict)
def get_sponsored_posts_analytics(
    period: str = Query("month", enum=["week", "month", "year"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get detailed sponsored posts analytics
    """
    current_time = datetime.utcnow()
    
    if period == "week":
        start_date = current_time - timedelta(days=7)
    elif period == "month":
        start_date = current_time - timedelta(days=30)
    else:  # year
        start_date = current_time - timedelta(days=365)
    
    # Daily breakdown
    daily_breakdown = []
    days = (current_time - start_date).days
    
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        daily_breakdown.append({
            "date": day_start.date().isoformat(),
            "created": db.query(SponsoredPost).filter(
                SponsoredPost.created_at >= day_start,
                SponsoredPost.created_at < day_end
            ).count(),
            "approved": db.query(SponsoredPost).filter(
                SponsoredPost.approved_at >= day_start,
                SponsoredPost.approved_at < day_end
            ).count()
        })
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": current_time.isoformat(),
        "daily_breakdown": daily_breakdown,
        "summary": {
            "total_created": db.query(SponsoredPost).filter(SponsoredPost.created_at >= start_date).count(),
            "total_approved": db.query(SponsoredPost).filter(SponsoredPost.approved_at >= start_date).count(),
            "pending": db.query(SponsoredPost).filter(
                SponsoredPost.is_approved == False,
                SponsoredPost.rejected_at == None
            ).count()
        }
    }


@router.get("/events/analytics", response_model=dict)
def get_events_analytics(
    period: str = Query("month", enum=["week", "month", "year"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get detailed events analytics
    """
    current_time = datetime.utcnow()
    
    if period == "week":
        start_date = current_time - timedelta(days=7)
    elif period == "month":
        start_date = current_time - timedelta(days=30)
    else:  # year
        start_date = current_time - timedelta(days=365)
    
    # Upcoming events count
    upcoming_events = db.query(Event).filter(
        Event.is_approved == True,
        Event.event_date >= current_time.date()
    ).count()
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": current_time.isoformat(),
        "total_events": db.query(Event).filter(Event.created_at >= start_date).count(),
        "approved_events": db.query(Event).filter(
            Event.is_approved == True,
            Event.created_at >= start_date
        ).count(),
        "upcoming_events": upcoming_events,
        "online_events": db.query(Event).filter(
            Event.is_online == True,
            Event.created_at >= start_date
        ).count(),
        "offline_events": db.query(Event).filter(
            Event.is_online == False,
            Event.created_at >= start_date
        ).count()
    }


@router.get("/polls/analytics", response_model=dict)
def get_polls_analytics(
    period: str = Query("month", enum=["week", "month", "year"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get detailed polls analytics
    """
    current_time = datetime.utcnow()
    
    if period == "week":
        start_date = current_time - timedelta(days=7)
    elif period == "month":
        start_date = current_time - timedelta(days=30)
    else:  # year
        start_date = current_time - timedelta(days=365)
    
    # Get all polls in period
    polls = db.query(Poll).filter(Poll.created_at >= start_date).all()
    
    total_votes = 0
    for poll in polls:
        if poll.votes:
            total_votes += sum(poll.votes)
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": current_time.isoformat(),
        "total_polls": len(polls),
        "approved_polls": db.query(Poll).filter(
            Poll.is_approved == True,
            Poll.created_at >= start_date
        ).count(),
        "active_polls": db.query(Poll).filter(
            Poll.is_approved == True,
            (Poll.expires_at == None) | (Poll.expires_at > current_time)
        ).count(),
        "total_votes": total_votes,
        "avg_votes_per_poll": round(total_votes / len(polls), 2) if len(polls) > 0 else 0
    }


# =========================================================
# QUICK STATS API (For Dashboard Widgets)
# =========================================================

@router.get("/quick-stats", response_model=dict)
def get_quick_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get quick statistics for dashboard widgets
    """
    current_time = datetime.utcnow()
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        "today": {
            "ads_created": db.query(Advertisement).filter(Advertisement.created_at >= today_start).count(),
            "posts_created": db.query(SponsoredPost).filter(SponsoredPost.created_at >= today_start).count(),
            "events_created": db.query(Event).filter(Event.created_at >= today_start).count(),
            "polls_created": db.query(Poll).filter(Poll.created_at >= today_start).count(),
        },
        "pending": {
            "ads": db.query(Advertisement).filter(
                Advertisement.is_approved == False,
                Advertisement.rejected_at == None
            ).count(),
            "posts": db.query(SponsoredPost).filter(
                SponsoredPost.is_approved == False,
                SponsoredPost.rejected_at == None
            ).count(),
            "events": db.query(Event).filter(Event.is_approved == False).count(),
            "polls": db.query(Poll).filter(Poll.is_approved == False).count(),
        },
        "active": {
            "ads": db.query(Advertisement).filter(
                Advertisement.is_approved == True,
                Advertisement.is_active == True,
                Advertisement.start_date <= current_time,
                Advertisement.end_date >= current_time
            ).count(),
            "posts": db.query(SponsoredPost).filter(
                SponsoredPost.is_approved == True,
                SponsoredPost.start_date <= current_time,
                SponsoredPost.end_date >= current_time
            ).count(),
            "events": db.query(Event).filter(
                Event.is_approved == True,
                Event.event_date >= current_time.date()
            ).count(),
            "polls": db.query(Poll).filter(
                Poll.is_approved == True,
                (Poll.expires_at == None) | (Poll.expires_at > current_time)
            ).count(),
        },
        "total": {
            "ads": db.query(Advertisement).count(),
            "posts": db.query(SponsoredPost).count(),
            "events": db.query(Event).count(),
            "polls": db.query(Poll).count(),
        }
    }
