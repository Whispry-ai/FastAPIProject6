"""
Enhanced Content Routes for Hyperlocal News Application
Missing critical endpoints for events, polls, and advertisements
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.content import Event, Poll, Advertisement
from auth.dependencies import get_current_user
from models.user import User as UserModel

router = APIRouter(prefix="/content", tags=["Content Enhanced"])

# Pydantic models
class PollVoteRequest(BaseModel):
    option_index: int

@router.get("/events")
def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    upcoming_only: bool = Query(True, description="Show only upcoming events"),
    db: Session = Depends(get_db)
):
    """
    Get events with filtering options
    """
    try:
        # Build query
        query = db.query(Event).filter(Event.is_approved == True)
        
        # Add location filters
        if city_id:
            query = query.filter(Event.city_id == city_id)
        elif district_id:
            query = query.filter(Event.district_id == district_id)
        elif state_id:
            query = query.filter(Event.state_id == state_id)
        
        # Filter by date
        if upcoming_only:
            query = query.filter(Event.event_date >= datetime.utcnow())
        
        # Add pagination
        offset = (page - 1) * limit
        total = query.count()
        events = query.order_by(Event.event_date).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "events": [
                {
                    "id": event.id,
                    "event_uid": event.event_uid,
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.event_date.isoformat() if event.event_date else None,
                    "location": event.location,
                    "image_url": event.image_url,
                    "organizer": event.organizer,
                    "contact_info": event.contact_info,
                    "ticket_url": event.ticket_url,
                    "is_free": event.is_free,
                    "price": event.price,
                    "city_id": event.city_id,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                }
                for event in events
            ],
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
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.get("/polls")
def get_polls(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    active_only: bool = Query(True, description="Show only active polls"),
    db: Session = Depends(get_db)
):
    """
    Get polls with voting options
    """
    try:
        # Build query
        query = db.query(Poll).filter(Poll.is_approved == True)
        
        # Filter by active status
        if active_only:
            query = query.filter(
                or_(
                    Poll.expires_at.is_(None),
                    Poll.expires_at >= datetime.utcnow()
                )
            )
        
        # Add pagination
        offset = (page - 1) * limit
        total = query.count()
        polls = query.order_by(desc(Poll.created_at)).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "polls": [
                {
                    "id": poll.id,
                    "poll_uid": poll.poll_uid,
                    "question": poll.question,
                    "options": poll.options,
                    "votes": poll.votes or {},
                    "user_uids_voted": poll.user_uids_voted or [],
                    "total_votes": sum(poll.votes.values()) if poll.votes else 0,
                    "expires_at": poll.expires_at.isoformat() if poll.expires_at else None,
                    "is_expired": poll.expires_at and poll.expires_at < datetime.utcnow(),
                    "created_at": poll.created_at.isoformat() if poll.created_at else None
                }
                for poll in polls
            ],
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
        raise HTTPException(status_code=500, detail=f"Failed to get polls: {str(e)}")

@router.post("/polls/{poll_id}/vote")
def vote_in_poll(
    poll_id: int,
    vote_request: PollVoteRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Vote in a poll
    """
    try:
        # Get poll
        poll = db.query(Poll).filter(Poll.id == poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        # Check if poll is active
        if poll.expires_at and poll.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Poll has expired")
        
        # Check if user already voted
        user_uids_voted = poll.user_uids_voted or []
        if current_user.user_uid in user_uids_voted:
            raise HTTPException(status_code=400, detail="You have already voted in this poll")
        
        # Validate option index
        options = poll.options or []
        if vote_request.option_index < 0 or vote_request.option_index >= len(options):
            raise HTTPException(status_code=400, detail="Invalid option index")
        
        # Update votes
        votes = poll.votes or {}
        option_key = str(vote_request.option_index)
        votes[option_key] = votes.get(option_key, 0) + 1
        
        # Update user voted list
        user_uids_voted.append(current_user.user_uid)
        
        # Save changes
        poll.votes = votes
        poll.user_uids_voted = user_uids_voted
        db.commit()
        
        return {
            "success": True,
            "message": "Vote recorded successfully",
            "poll": {
                "id": poll.id,
                "question": poll.question,
                "total_votes": sum(votes.values()),
                "your_vote": {
                    "option_index": vote_request.option_index,
                    "option_text": options[vote_request.option_index]
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vote: {str(e)}")

@router.get("/advertisements")
def get_advertisements(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    active_only: bool = Query(True, description="Show only active ads"),
    db: Session = Depends(get_db)
):
    """
    Get advertisements with filtering options
    """
    try:
        # Build query
        query = db.query(Advertisement).filter(Advertisement.is_approved == True)
        
        # Add location filters
        if city_id:
            query = query.filter(Advertisement.city_id == city_id)
        elif district_id:
            query = query.filter(Advertisement.district_id == district_id)
        elif state_id:
            query = query.filter(Advertisement.state_id == state_id)
        
        # Filter by active status
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    Advertisement.start_date <= now,
                    Advertisement.end_date >= now
                )
            )
        
        # Add pagination
        offset = (page - 1) * limit
        total = query.count()
        ads = query.order_by(desc(Advertisement.created_at)).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "advertisements": [
                {
                    "id": ad.id,
                    "title": ad.title,
                    "content": ad.content,
                    "image_url": ad.image_url,
                    "cta_text": ad.cta_text,
                    "cta_url": ad.redirect_url,
                    "start_date": ad.start_date.isoformat() if ad.start_date else None,
                    "end_date": ad.end_date.isoformat() if ad.end_date else None,
                    "state_id": ad.state_id,
                    "district_id": ad.district_id,
                    "city_id": ad.city_id,
                    "target_gender": ad.target_gender,
                    "target_age_min": ad.target_age_min,
                    "target_age_max": ad.target_age_max,
                    "is_active": (
                        ad.start_date <= datetime.utcnow() <= ad.end_date
                        if ad.start_date and ad.end_date else False
                    ),
                    "created_at": ad.created_at.isoformat() if ad.created_at else None
                }
                for ad in ads
            ],
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
        raise HTTPException(status_code=500, detail=f"Failed to get advertisements: {str(e)}")

@router.get("/stats")
def get_content_stats(
    db: Session = Depends(get_db)
):
    """
    Get content statistics
    """
    try:
        now = datetime.utcnow()
        
        # Event statistics
        total_events = db.query(Event).filter(Event.is_approved == True).count()
        upcoming_events = db.query(Event).filter(
            and_(
                Event.is_approved == True,
                Event.event_date >= now
            )
        ).count()
        
        # Poll statistics
        total_polls = db.query(Poll).filter(Poll.is_approved == True).count()
        active_polls = db.query(Poll).filter(
            and_(
                Poll.is_approved == True,
                or_(
                    Poll.expires_at.is_(None),
                    Poll.expires_at >= now
                )
            )
        ).count()
        
        # Advertisement statistics
        total_ads = db.query(Advertisement).filter(Advertisement.is_approved == True).count()
        active_ads = db.query(Advertisement).filter(
            and_(
                Advertisement.is_approved == True,
                Advertisement.start_date <= now,
                Advertisement.end_date >= now
            )
        ).count()
        
        return {
            "success": True,
            "timestamp": now.isoformat(),
            "events": {
                "total": total_events,
                "upcoming": upcoming_events,
                "past": total_events - upcoming_events
            },
            "polls": {
                "total": total_polls,
                "active": active_polls,
                "expired": total_polls - active_polls
            },
            "advertisements": {
                "total": total_ads,
                "active": active_ads,
                "scheduled": total_ads - active_ads
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content stats: {str(e)}")
