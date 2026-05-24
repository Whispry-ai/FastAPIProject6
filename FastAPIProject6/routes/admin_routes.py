# routes/admin_routes.py
"""
Admin Routes for Hyperlocal News API.
Provides endpoints for:
- News moderation (approve/reject)
- Category, user, and content management
- Dashboard stats and reports
"""
from datetime import datetime, timedelta, timezone
import random
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Query, status
from grpc import Status
from requests import Session
import requests
from sqlalchemy import desc, func, or_

from auth.dependencies import admin_required, get_current_user, require_role
from auth.jwt_handler import create_access_token
from database import get_db
from gemini_ai import call_gemini_api_english, call_gemini_api_telugu
from models.base_location import City, District, Language, State
from models.news import Category, News
from models.user import User, UserPreference
from models.content import AdImpression, Advertisement, Event, Poll, SponsoredPost, YouTubeShort
from models.engagement import Notification
from schemas import AdminDashboardOut, AdminEngagementOut, AdminLoginRequest, AdminNewsAnalyticsOut, AdminNewsDetailsOut, AdminNewsItemOut, AdminNotificationRequest, AutoNewsCreate, RoleAssignRequest, UserRole, VideoItem
import schemas
from sqlalchemy.orm import (
    Session, joinedload
)
from celery_worker import send_news_notification

from utility import YOUTUBE_API_KEY, YOUTUBE_SEARCH_URL, extract_source_name, fetch_article_text_and_image, generate_news_uid, generate_unique_username, generate_user_uid

router = APIRouter(prefix="/admin", tags=["Admins"])

# =====================================================================
# Admin Dashboard Overview
# =====================================================================
@router.get("/admin/dashboard", response_model=AdminDashboardOut, tags=["Admin"])
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    today = datetime.now(timezone.utc).date()

    # NEWS
    total_news = db.query(func.count(News.id)).scalar()
    news_today = db.query(func.count(News.id)).filter(
        func.date(News.created_at) == today
    ).scalar()

    pending_news = db.query(func.count(News.id)).filter(
        News.is_approved == 0
    ).scalar()

    rejected_news = db.query(func.count(News.id)).filter(
        News.is_approved == 2
    ).scalar()

    # USERS
    total_users = db.query(func.count(User.id)).scalar()
    users_today = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()

    # ADS
    total_ads = db.query(func.count(Advertisement.id)).scalar()

    # EVENTS
    total_events = db.query(func.count(Event.id)).scalar()

    # POLLS
    total_polls = db.query(func.count(Poll.id)).scalar()

    # ENGAGEMENT
    total_views = db.query(func.sum(News.views_count)).scalar() or 0
    total_likes = db.query(func.sum(News.likes_count)).scalar() or 0
    total_comments = db.query(func.sum(News.comments_count)).scalar() or 0
    total_shares = db.query(func.sum(News.shares_count)).scalar() or 0

    # TOP REPORTERS
    reporters = (
        db.query(
            User.user_uid,
            User.name,
            func.count(News.id).label("news_count")
        )
        .join(News, News.user_uid == User.user_uid)
        .group_by(User.user_uid, User.name)
        .order_by(func.count(News.id).desc())
        .limit(5)
        .all()
    )

    top_reporters = [
        {
            "user_uid": r.user_uid,
            "name": r.name,
            "news_count": r.news_count
        }
        for r in reporters
    ]

    # TRENDING NEWS (based on views)
    trending = (
        db.query(News.news_uid, News.title, News.views_count)
        .filter(News.is_approved == 1)
        .order_by(News.views_count.desc())
        .limit(5)
        .all()
    )

    trending_news = [
        {
            "news_uid": t.news_uid,
            "title": t.title,
            "views": t.views_count
        }
        for t in trending
    ]

    return AdminDashboardOut(
        news={
            "total": total_news,
            "today": news_today
        },
        users={
            "total": total_users,
            "today": users_today
        },
        ads={
            "total": total_ads
        },
        events={
            "total": total_events
        },
        polls={
            "total": total_polls
        },
        engagement={
            "views": total_views,
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares
        },
        pending_news=pending_news,
        rejected_news=rejected_news,
        top_reporters=top_reporters,
        trending_news=trending_news
    )
@router.get("/admin/stats/detailed", tags=["Admin"])
def get_detailed_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get detailed admin statistics"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    # =========================================================
    # 1. USER STATISTICS
    # =========================================================
    
    # New users (registered in last 7 days)
    new_users = db.query(User).filter(User.created_at >= week_ago).count()
    
    # Active users (users who posted news in last 7 days)
    # Using direct count on News table to avoid join ambiguity
    active_users = db.query(func.count(func.distinct(News.user_uid))).filter(
        News.created_at >= week_ago,
        News.is_approved == 1
    ).scalar() or 0
    
    # =========================================================
    # 2. CONTENT TRENDS
    # =========================================================
    
    news_by_language = db.query(
        Language.name,
        func.count(News.id).label('count')
    ).join(News, News.language_id == Language.id).filter(
        News.created_at >= week_ago,
        News.is_approved == 1
    ).group_by(Language.name).all()
    
    # =========================================================
    # 3. AD PERFORMANCE
    # =========================================================
    
    ad_performance = []
    try:
        # Check if AdImpression table exists
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        if 'ad_impressions' in inspector.get_table_names():
            ad_performance = db.query(
                Advertisement.placement,
                func.count(AdImpression.id).label('impressions')
            ).join(AdImpression, AdImpression.ad_id == Advertisement.id).filter(
                AdImpression.impression_at >= week_ago
            ).group_by(Advertisement.placement).all()
            
            ad_performance = [{"placement": p.placement, "impressions": p.impressions} for p in ad_performance]
    except Exception as e:
        print(f"Ad performance query error: {e}")
    
    # =========================================================
    # 4. ENGAGEMENT SUMMARY
    # =========================================================
    
    total_views = db.query(func.sum(News.views_count)).filter(
        News.created_at >= week_ago
    ).scalar() or 0
    
    total_likes = db.query(func.sum(News.likes_count)).filter(
        News.created_at >= week_ago
    ).scalar() or 0
    
    # =========================================================
    # 5. RETURN RESPONSE
    # =========================================================
    
    return {
        "period": "last_7_days",
        "user_stats": {
            "new_users": new_users,
            "active_users": active_users,
            "total_users": db.query(User).count()
        },
        "content_stats": {
            "news_by_language": [{"language": l.name, "count": l.count} for l in news_by_language],
            "total_views": total_views,
            "total_likes": total_likes
        },
        "ad_performance": ad_performance
    }
@router.get("/admin/export/news", tags=["Admin"])
def export_news(
    format: str = Query("csv", enum=["csv", "json"]),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Export news data"""
    query = db.query(News)
    
    if date_from:
        query = query.filter(News.created_at >= date_from)
    if date_to:
        query = query.filter(News.created_at <= date_to)
    
    news = query.all()
    
    if format == "csv":
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["News UID", "Title", "Created At", "Views", "Likes", "Status"])
        
        for n in news:
            writer.writerow([
                n.news_uid, n.title, n.created_at, n.views_count, 
                n.likes_count, "Approved" if n.is_approved == 1 else "Pending"
            ])
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=news_export.csv"}
        )
    
    return {"news": news, "count": len(news)}   
@router.get("/admin/news/analytics", response_model=AdminNewsAnalyticsOut, tags=["Admin"])
def get_news_analytics(
    days: int = Query(7, description="Analytics window (7 or 30 days)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily news + engagement
    metrics = (
        db.query(
            func.date(News.created_at).label("date"),
            func.count(News.id).label("news_posted"),
            func.sum(News.views_count).label("views"),
            func.sum(News.likes_count).label("likes"),
            func.sum(News.comments_count).label("comments"),
            func.sum(News.shares_count).label("shares"),
        )
        .filter(News.created_at >= start_date)
        .group_by(func.date(News.created_at))
        .order_by(func.date(News.created_at))
        .all()
    )

    daily_metrics = [
        {
            "date": str(m.date),
            "news_posted": m.news_posted or 0,
            "views": m.views or 0,
            "likes": m.likes or 0,
            "comments": m.comments or 0,
            "shares": m.shares or 0,
        }
        for m in metrics
    ]

    # User growth
    users = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("new_users")
        )
        .filter(User.created_at >= start_date)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )

    user_growth = [
        {
            "date": str(u.date),
            "new_users": u.new_users
        }
        for u in users
    ]

    return {
        "daily_metrics": daily_metrics,
        "user_growth": user_growth
    }
# =====================================================================
# News Moderation Routes
# =====================================================================
@router.get("/admin/news/pending", response_model=dict, tags=["Admin"])
def get_pending_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    language_id: Optional[int] = Query(None),
    state_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    city_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, min_length=2),
    sort_by: str = Query("created_at", enum=["created_at", "title"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Simplified version - Get pending news with pagination"""
    
    query = db.query(News).filter(News.is_approved == 0)
    
    # Apply filters
    if language_id:
        query = query.filter(News.language_id == language_id)
    
    if city_id:
        query = query.filter(News.city_id == city_id)
    elif district_id:
        query = query.join(City, News.city_id == City.id).filter(City.district_id == district_id)
    elif state_id:
        query = query.join(City, News.city_id == City.id).join(District, City.district_id == District.id).filter(District.state_id == state_id)
    
    if category_id:
        query = query.join(News.categories).filter(Category.id == category_id)
    
    if search:
        query = query.filter(
            or_(
                News.title.ilike(f"%{search}%"),
                News.summary.ilike(f"%{search}%")
            )
        )
    
    # Apply sorting
    if sort_by == "created_at":
        sort_column = News.created_at
    else:
        sort_column = News.title
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    pending_news = query.offset(offset).limit(limit).all()
    
    # Build response
    items = []
    for news in pending_news:
        # Get reporter name separately
        reporter = db.query(User).filter(User.user_uid == news.user_uid).first()
        
        items.append({
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary[:200] if news.summary else None,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "reporter_name": reporter.name if reporter else None,
            "language_id": news.language_id,
            "city_id": news.city_id
        })
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }

# =====================================================================
# Admin Assign Roles
# =====================================================================
@router.post("/admin/assign-role",tags=["Admin"])
def assign_role(
    payload: RoleAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can assign roles
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can assign roles")

    # Target user
    user = db.query(User).filter(User.user_uid == payload.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update role
    try:
        new_role = UserRole(payload.new_role)  # Validates role
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = new_role
    db.commit()

    return {"message": f"Role of user {user.id} updated to {new_role.name}"}


@router.post("/token/admin-login",tags=["Auth"])
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    # Fetch user by email or mobile
    user = db.query(User).filter(
        (User.email == payload.identifier) | (User.phone == payload.identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if str(user.role) != str(payload.role):
        raise HTTPException(status_code=403, detail="Role mismatch")

    # ✅ Use user_uid instead of database ID
    token_data = {
        "sub": user.user_uid,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }
# =====================================================================
# AUTO GENERATE
# # =====================================================================


@router.post("/news/auto-generate-te", response_model=schemas.NewsOut, tags=["Admin"])
def auto_generate_news_telugu(
    data: AutoNewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    user_uid = current_user.user_uid

    # ✅ Validate user
    user = db.query(User).filter_by(user_uid=user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Validate state/district/city only if provided
    state = None
    if data.state_id:
        state = db.query(State).filter_by(id=data.state_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")

    district = None
    if data.district_id:
        district = db.query(District).filter_by(id=data.district_id).first()
        if not district:
            raise HTTPException(status_code=404, detail="District not found")

    city = None
    if data.city_id:
        city = db.query(City).filter_by(id=data.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")

    # ✅ Extract article text & image
    article_data = fetch_article_text_and_image(data.source_url)
    article_text = article_data.get("text")
    image_url = article_data.get("image_url")

    # ✅ AI Generate Telugu title & summary
    ai_result = call_gemini_api_telugu(article_text)
    if not ai_result.get("title") or not ai_result.get("summary"):
        raise HTTPException(status_code=500, detail="Gemini AI failed to generate Telugu content")

    # ✅ Unique news UID
    news_uid = generate_news_uid()

    # ✅ Get Telugu language row
    telugu_language = db.query(Language).filter_by(code="te").first()
    if not telugu_language:
        raise HTTPException(status_code=500, detail="Telugu language not found in DB")

    # ✅ Create News object
    new_news = News(
        news_uid=news_uid,
        title=ai_result["title"],
        summary=ai_result["summary"],
        image_url=image_url,
        language_id=telugu_language.id,
        user_uid=user_uid,
        city_id=city.id if city else None,   # optional city_id
        is_auto_generated=True,
        source_url=data.source_url or None,
        source_name=extract_source_name(data.source_url) if data.source_url else None,
    )

    db.add(new_news)
    db.commit()
    db.refresh(new_news)

    # ✅ Assign categories if provided
    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        new_news.categories = categories
        db.commit()
        db.refresh(new_news)

    # ✅ Build clean response (convert ORM → plain dicts)
    return schemas.NewsOut(
    news_uid=new_news.news_uid,
    title=new_news.title,
    summary=new_news.summary,
    image_url=new_news.image_url,
    language=schemas.LanguageOut.model_validate(new_news.language, from_attributes=True).model_dump() if new_news.language else None,  # ✅ fixed
    user_uid=new_news.user_uid,
    is_approved=new_news.is_approved,
    created_at=new_news.created_at.isoformat() if new_news.created_at else None,
    city=schemas.CityOut.model_validate(new_news.city, from_attributes=True).model_dump() if new_news.city else None,
    district=schemas.DistrictOut.model_validate(new_news.city.district, from_attributes=True).model_dump() if (new_news.city and new_news.city.district) else None,
    state=schemas.StateOut.model_validate(new_news.city.district.state, from_attributes=True).model_dump() if (new_news.city and new_news.city.district and new_news.city.district.state) else None,
    source_url=new_news.source_url,
    source_name=new_news.source_name,
    category_ids=[c.id for c in new_news.categories] if new_news.categories else [],
)
@router.post("/news/auto-generate-en", response_model=schemas.NewsOut, tags=["Admin"])
def auto_generate_news_english(
    data: schemas.AutoNewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    user_uid = current_user.user_uid

    # ✅ Validate user
    user = db.query(User).filter_by(user_uid=user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Validate state/district/city only if provided
    state = None
    if data.state_id:
        state = db.query(State).filter_by(id=data.state_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")

    district = None
    if data.district_id:
        district = db.query(District).filter_by(id=data.district_id).first()
        if not district:
            raise HTTPException(status_code=404, detail="District not found")

    city = None
    if data.city_id:
        city = db.query(City).filter_by(id=data.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")

    # ✅ Extract article text & image
    article_data = fetch_article_text_and_image(data.source_url)
    article_text = article_data.get("text")
    image_url = article_data.get("image_url")

    # ✅ AI Generate English title & summary (translated if needed)
    ai_result = call_gemini_api_english(article_text)
    if not ai_result.get("title") or not ai_result.get("summary"):
        raise HTTPException(status_code=500, detail="Gemini AI failed to generate English content")

    # ✅ Unique news UID
    news_uid = generate_news_uid()

    # ✅ Get English language row
    english_language = db.query(Language).filter_by(code="en").first()
    if not english_language:
        raise HTTPException(status_code=500, detail="English language not found in DB")

    # ✅ Create News object
    new_news = News(
        news_uid=news_uid,
        title=ai_result["title"],
        summary=ai_result["summary"],
        image_url=image_url,
        language_id=english_language.id,
        user_uid=user_uid,
        city_id=city.id if city else None,  # optional city_id
        is_auto_generated=True,
        source_url=data.source_url or None,
        source_name=extract_source_name(data.source_url) if data.source_url else None,
    )

    db.add(new_news)
    db.commit()
    db.refresh(new_news)

    # ✅ Assign categories if provided
    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        new_news.categories = categories
        db.commit()
        db.refresh(new_news)

    # ✅ Build clean response
    return schemas.NewsOut(
        news_uid=new_news.news_uid,
        title=new_news.title,
        summary=new_news.summary,
        image_url=new_news.image_url,
        language=schemas.LanguageOut.model_validate(new_news.language, from_attributes=True).model_dump() if new_news.language else None,
        user_uid=new_news.user_uid,
        is_approved=new_news.is_approved,
        created_at=new_news.created_at.isoformat() if new_news.created_at else None,
        city=schemas.CityOut.model_validate(new_news.city, from_attributes=True).model_dump() if new_news.city else None,
        district=schemas.DistrictOut.model_validate(new_news.city.district, from_attributes=True).model_dump() if (new_news.city and new_news.city.district) else None,
        state=schemas.StateOut.model_validate(new_news.city.district.state, from_attributes=True).model_dump() if (new_news.city and new_news.city.district and new_news.city.district.state) else None,
        source_url=new_news.source_url,
        source_name=new_news.source_name,
        category_ids=[c.id for c in new_news.categories] if new_news.categories else [],
    )


# =====================================================================
# Single News Details
# =====================================================================

@router.get("/admin/news/pending-list", response_model=dict, tags=["Admin"])
def get_pending_news_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    language_id: Optional[int] = Query(None),
    state_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    city_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, min_length=2),
    sort_by: str = Query("created_at", enum=["created_at", "title"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Simplified version - Get pending news with pagination"""
    
    query = db.query(News).filter(News.is_approved == 0)
    
    # Apply filters
    if language_id:
        query = query.filter(News.language_id == language_id)
    
    if city_id:
        query = query.filter(News.city_id == city_id)
    elif district_id:
        query = query.join(City, News.city_id == City.id).filter(City.district_id == district_id)
    elif state_id:
        query = query.join(City, News.city_id == City.id).join(District, City.district_id == District.id).filter(District.state_id == state_id)
    
    if category_id:
        query = query.join(News.categories).filter(Category.id == category_id)
    
    if search:
        query = query.filter(
            or_(
                News.title.ilike(f"%{search}%"),
                News.summary.ilike(f"%{search}%")
            )
        )
    
    # Apply sorting
    if sort_by == "created_at":
        sort_column = News.created_at
    else:
        sort_column = News.title
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    pending_news = query.offset(offset).limit(limit).all()
    
    # Build response
    items = []
    for news in pending_news:
        # Get reporter name separately
        reporter = db.query(User).filter(User.user_uid == news.user_uid).first()
        
        items.append({
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary[:200] if news.summary else None,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "reporter_name": reporter.name if reporter else None,
            "language_id": news.language_id,
            "city_id": news.city_id
        })
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }
# =====================================================================
# Approve / Reject News
# =====================================================================
@router.get("/admin/news/{news_uid}", response_model=dict, tags=["Admin"])
def get_news_by_id(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get detailed news information by news_uid"""
    
    news = db.query(News).options(
        joinedload(News.categories),
        joinedload(News.user),
        joinedload(News.approver),
        joinedload(News.language),
        joinedload(News.city).joinedload(City.district).joinedload(District.state)
    ).filter(News.news_uid == news_uid).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # =========================================================
    # GET LOCATION HIERARCHY
    # =========================================================
    
    city = news.city
    district = city.district if city else None
    state = district.state if district else None
    
    # =========================================================
    # GET REPORTER INFO
    # =========================================================
    
    reporter = news.user
    reporter_info = {
        "user_uid": reporter.user_uid if reporter else None,
        "name": reporter.name if reporter else None,
        "user_name": reporter.user_name if reporter else None,
        "email": reporter.email if reporter else None,
        "phone": reporter.phone if reporter else None,
        "mobile": reporter.phone if reporter else None,
        "role": reporter.role if reporter else None,
        "role_name": _get_role_name(reporter.role) if reporter else None,
        "created_at": reporter.created_at.isoformat() if reporter and reporter.created_at else None
    } if reporter else None
    
    # =========================================================
    # GET APPROVER INFO
    # =========================================================
    
    approver_info = None
    if news.approved_by_uid:
        approver = news.approver
        if approver:
            approver_info = {
                "user_uid": approver.user_uid,
                "name": approver.name,
                "user_name": approver.user_name,
                "email": approver.email,
                "phone": approver.phone,
                "mobile": approver.phone,
                "role": approver.role,
                "role_name": _get_role_name(approver.role),
                "approved_at": news.approved_at.isoformat() if hasattr(news, 'approved_at') and news.approved_at else None
            }
    
    # =========================================================
    # GET CATEGORIES
    # =========================================================
    
    categories = [
        {"id": c.id, "name": c.name}
        for c in news.categories
    ] if news.categories else []
    
    # =========================================================
    # GET LANGUAGE
    # =========================================================
    
    language_info = {
        "id": news.language.id if news.language else None,
        "name": news.language.name if news.language else None,
        "code": news.language.code if news.language else None
    } if news.language else None
    
    # =========================================================
    # GET STATUS
    # =========================================================
    
    status = "pending"
    if news.is_approved == 1:
        status = "approved"
    elif news.is_approved == 2:
        status = "rejected"
    
    # =========================================================
    # BUILD RESPONSE
    # =========================================================
    
    return {
        "news_uid": news.news_uid,
        "title": news.title,
        "summary": news.summary,
        "image_url": news.image_url,
        "created_at": news.created_at.isoformat() if news.created_at else None,
        "status": status,
        "is_approved": news.is_approved,
        "is_breaking": news.is_breaking,
        
        "language": language_info,
        
        "location": {
            "city": city.name if city else None,
            "district": district.name if district else None,
            "state": state.name if state else None
        },
        
        "source": {
            "name": news.source_name,
            "url": news.source_url
        },
        
        "categories": categories,
        
        "reporter": reporter_info,
        "approver": approver_info,
        
        "engagement": {
            "views": news.views_count or 0,
            "likes": news.likes_count or 0,
            "comments": news.comments_count or 0,
            "shares": news.shares_count or 0
        },
        
        "timestamps": {
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "approved_at": news.approved_at.isoformat() if hasattr(news, 'approved_at') and news.approved_at else None,
            "rejected_at": news.rejected_at.isoformat() if news.rejected_at else None
        }
    }


def _get_role_name(role: int) -> str:
    """Get role name from role integer"""
    roles = {
        0: "Guest",
        1: "User",
        2: "Publisher",
        3: "Employee",
        4: "Admin"
    }
    return roles.get(role, "Unknown")

@router.get("/admin/news-shorts/telugu", response_model=List[VideoItem], tags=["Admin"])
def fetch_and_store_telugu_shorts(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)  # Enforces admin token & role
):
    return fetch_and_store_shorts_by_language("telugu news", "te", db)


@router.get("/news1/{news_uid}", response_model=AdminNewsDetailsOut)
def get_admin_news_details(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    news = db.query(News).filter(News.news_uid == news_uid).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    posted_user = db.query(User).filter(User.user_uid == news.user_uid).first()

    approver = None
    if news.approved_by_uid:
        approver = db.query(User).filter(User.user_uid == news.approved_by_uid).first()

    language_obj = None
    if news.language:
        language_obj = {
            "id": news.language.id,
            "code": news.language.code,
            "name": news.language.name
        }

    category_names = [c.name for c in news.categories] if news.categories else []

    city_name = news.city.name if news.city else None
    district_name = news.city.district.name if news.city and news.city.district else None
    state_name = news.city.district.state.name if news.city and news.city.district and news.city.district.state else None

    response = {
        "news_uid": news.news_uid,
        "title": news.title,
        "summary": news.summary,
        "image_url": news.image_url,
        "language": language_obj,
        "is_approved": news.is_approved,
        "source_url": news.source_url,
        "source_name": news.source_name,
        "created_at": news.created_at,
        "category_names": category_names,
        "state": state_name,
        "district": district_name,
        "city": city_name,
        "user_name": posted_user.name if posted_user else None,
        "posted_by": {
            "user_uid": posted_user.user_uid,
            "name": posted_user.name,
            "phone": posted_user.phone
        } if posted_user else None,
        "approved_by": {
            "user_uid": approver.user_uid,
            "name": approver.name,
            "phone": approver.phone
        } if approver else None,

        # IMPORTANT: engagement must always exist
        "engagement": {
            "likes": news.likes_count or 0,
            "comments": news.comments_count or 0,
            "shares": news.shares_count or 0,
            "views": news.views_count or 0
        }
    }

    return response
    
    
def send_reject_notification(user: User, news: News, reason: str = None):
    """
    Dummy function to send push/app notification.
    Replace with your actual FCM/OneSignal/Expo push logic.
    """
    message = f"Your news '{news.title}' was rejected."
    if reason:
        message += f" Reason: {reason}"
    print(f"📢 Sending notification to {user.phone}: {message}")



@router.put("/admin/news/{news_uid}/reject", status_code=status.HTTP_200_OK, tags=["Admin"])
def reject_news_simple(
    news_uid: str,
    reason: Optional[str] = Query(None, max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Simplified reject news API"""
    
    news = db.query(News).filter(News.news_uid == news_uid).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.is_approved == 1:
        raise HTTPException(status_code=400, detail="Cannot reject approved news")
    
    if news.is_approved == 2:
        return {"message": "News already rejected"}
    
    # Update news
    news.is_approved = 2
    news.rejected_at = datetime.utcnow()
    
    if reason:
        news.rejection_reason = reason
    
    db.commit()
    
    return {
        "message": "News rejected successfully",
        "news_uid": news.news_uid,
        "rejected_at": news.rejected_at.isoformat(),
        "rejection_reason": news.rejection_reason
    }
@router.get("/news/rejected", response_model=dict, tags=["Admin"])
def get_rejected_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get all rejected news with pagination."""
    
    offset = (page - 1) * limit
    
    rejected_news = db.query(News).filter(
        News.is_approved == 2
    ).order_by(desc(News.created_at)).offset(offset).limit(limit).all()
    
    total = db.query(News).filter(News.is_approved == 2).count()
    
    items = []
    for news in rejected_news:
        # Get reporter
        reporter = db.query(User).filter(User.user_uid == news.user_uid).first()
        
        # Get rejector (if you have this info stored elsewhere)
        # For now, we'll just show that it was rejected
        rejector_info = {
            "user_uid": None,
            "name": "Admin",
            "role_name": "Admin"
        }
        
        items.append({
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary[:150] if news.summary else None,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "rejected_at": None,
            "rejection_reason": None,
            "reporter": {
                "user_uid": reporter.user_uid if reporter else None,
                "name": reporter.name if reporter else None
            },
            "rejected_by": rejector_info,
            "location": {
                "city": news.city.name if news.city else None,
                "district": news.city.district.name if news.city and news.city.district else None,
                "state": news.city.district.state.name if news.city and news.city.district and news.city.district.state else None
            },
            "language": news.language.name if news.language else None
        })
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "metadata": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
@router.post("/admin/news/bulk-reject", status_code=status.HTTP_200_OK, tags=["Admin"])
def bulk_reject_news(
    news_uids: List[str] = Query(..., description="List of news UIDs to reject"),
    reason: Optional[str] = Query(None, max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    Bulk reject multiple news items.
    Admin only access.
    """
    
    results = {
        "successful": [],
        "failed": [],
        "total": len(news_uids)
    }
    
    for news_uid in news_uids:
        try:
            news = db.query(News).filter(News.news_uid == news_uid).first()
            
            if not news:
                results["failed"].append({
                    "news_uid": news_uid,
                    "reason": "News not found"
                })
                continue
            
            if news.is_approved == 1:
                results["failed"].append({
                    "news_uid": news_uid,
                    "reason": "Already approved"
                })
                continue
            
            if news.is_approved == 2:
                results["failed"].append({
                    "news_uid": news_uid,
                    "reason": "Already rejected"
                })
                continue
            
            # Reject the news
            news.is_approved = 2
            news.rejected_at = datetime.utcnow()
            news.updated_at = datetime.utcnow()
            
            if reason:
                news.rejection_reason = reason
            
            # Track who rejected
            if hasattr(news, 'rejected_by_uid'):
                news.rejected_by_uid = current_user.user_uid
            
            results["successful"].append({
                "news_uid": news_uid,
                "title": news.title
            })
            
        except Exception as e:
            results["failed"].append({
                "news_uid": news_uid,
                "reason": str(e)
            })
    
    db.commit()
    
    return {
        "message": f"Bulk reject completed: {len(results['successful'])} successful, {len(results['failed'])} failed",
        "results": results
    }

@router.put("/news/{news_uid}/approve", status_code=status.HTTP_200_OK, tags=["Admin", "Publisher"])
def approve_news(
    news_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER)),
):
    """
    Approve a news item identified by news_uid.
    Only users with role >= PUBLISHER (including ADMIN) can approve.
    """

    # 1️⃣ Fetch news
    news = db.query(News).filter(News.news_uid == news_uid).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    if news.is_approved == 1:
        return {"message": "News already approved"}

    # 2️⃣ Approve news
    news.is_approved = 1
    news.approved_by_uid = current_user.user_uid

    db.commit()
    db.refresh(news)

    # 3️⃣ Fetch approver info
    approver = db.query(User).filter(User.user_uid == news.approved_by_uid).first()

    approver_info = {
        "user_uid": approver.user_uid if approver else current_user.user_uid,
        "name": approver.name if approver else getattr(current_user, "name", "Unknown"),
        "phone": approver.phone if approver else getattr(current_user, "phone", None),
        "message": "You approved this post"
    }

    # 4️⃣ Send notification task to Celery
    send_news_notification.delay(news.news_uid, news.title)

    # 5️⃣ Return response immediately
    return {
        "message": "News approved. Notifications will be sent in background.",
        "news_uid": news.news_uid,
        "approved_by": approver_info,
    }
    
@router.get("/admin/news-shorts/english", response_model=List[VideoItem], tags=["Admin"])
def fetch_and_store_english_shorts(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)  # Enforces admin token & role
):
    return fetch_and_store_shorts_by_language("english news", "en", db)

def fetch_and_store_shorts_by_language(query: str, lang: str, db: Session):
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "maxResults": 5,
        "type": "video",
        "videoDuration": "short",
        "order": "date",
        "videoEmbeddable": "true"
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()
    result = []

    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            existing = db.query(YouTubeShort).filter_by(video_id=video_id).first()
            if existing:
                continue

            short = YouTubeShort(
                video_id=video_id,
                title=snippet["title"],
                thumbnail_url=snippet["thumbnails"]["high"]["url"],
                channel_title=snippet["channelTitle"],
                published_at=snippet["publishedAt"],
                video_url=f"https://www.youtube.com/watch?v={video_id}",
                language=lang  # ✅ IMPORTANT: Language column
            )
            db.add(short)
            db.commit()

            result.append(VideoItem(
                title=short.title,
                video_id=short.video_id,
                thumbnail_url=short.thumbnail_url,
                channel_title=short.channel_title,
                published_at=short.published_at.isoformat(),
            ))

    return result


# =====================================================================
# Admin Notifications
# =====================================================================
@router.post("/admin/send", response_model=dict,tags=["Admin"])
def send_admin_notification(
    data: AdminNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),  # Only admins allowed
):
    query = db.query(User)

    # Filter users based on target
    if data.target_type == "all":
        users = query.all()
    elif data.target_type == "state":
        users = query.filter(User.state == data.target_value).all()
    elif data.target_type == "district":
        users = query.filter(User.district == data.target_value).all()
    elif data.target_type == "city":
        users = query.filter(User.city == data.target_value).all()
    elif data.target_type == "user":
        users = query.filter(User.user_uid == data.target_value).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid target_type")

    if not users:
        return {"status": "No users found for target"}

    for user in users:
        notification = Notification(
            user_uid=user.user_uid,
            title=data.title,
            message=data.message,
            link_url=data.link_url,
            notification_type="custom"
        )
        db.add(notification)

    db.commit()
    return {"status": f"Sent to {len(users)} user(s)"}


# =====================================================================
# Admin Users Management
# =====================================================================
@router.get("/users", summary="List all registered users")
def get_all_users(db: Session = Depends(get_db)):
    """Retrieve all registered users."""
    return db.query(User).all()

@router.delete("/users/{user_uid}", summary="Delete a user")
def delete_user(user_uid: str, db: Session = Depends(get_db)):
    """Delete a user by UID (Admin privilege)."""
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_uid} deleted successfully"}
#__-----------------------------------------------------------------FEEDS ADMIN _------------------

@router.get("/feedsAdmin", response_model=List[dict], tags=["Admin"])
def get_feed(
    language: Optional[str] = Query(None),
    city_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EMPLOYEE)),  # Admin & Employee only
):
    now = datetime.utcnow()

    # Query approved news with eager loading
    news_query = (
        db.query(News)
        .options(
            joinedload(News.approver),
            joinedload(News.user),
            joinedload(News.city).joinedload(City.district).joinedload(District.state),
            joinedload(News.categories),
        )
        .filter(News.is_approved == 1)
    )

    if language:
        news_query = news_query.join(Language).filter(Language.code == language)
    if city_id:
        news_query = news_query.filter(News.city_id == city_id)

    news_list = news_query.order_by(News.created_at.desc()).limit(30).all()

    # Active sponsored posts
    sponsored_posts = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= now,
        SponsoredPost.end_date >= now
    ).all()
    random.shuffle(sponsored_posts)

    # Active ads
    ads = db.query(Advertisement).filter(
        Advertisement.is_active == True,
        Advertisement.start_date <= now,
        Advertisement.end_date >= now
    ).all()
    random.shuffle(ads)

    feed = []
    sponsor_idx = 0
    ad_idx = 0

    news_count = 0  # Track only news items for ad placement
    
    for i, news in enumerate(news_list):
        posted_by = db.query(User).filter_by(user_uid=news.user_uid).first()
        approved_by = db.query(User).filter_by(user_uid=news.approved_by_uid).first() if news.approved_by_uid else None

        # Get location names
        city_name = news.city.name if news.city else None
        district_name = news.city.district.name if news.city and news.city.district else None
        state_name = news.city.district.state.name if news.city and news.city.district and news.city.district.state else None

        # Get categories
        categories = [cat.name for cat in news.categories] if news.categories else []

        # User info for posted_by
        posted_by_info = None
        if posted_by:
            posted_by_info = {
                "user_uid": posted_by.user_uid,
                "name": posted_by.name,
                "user_name": posted_by.user_name,
                "role": posted_by.role
            }

        # User info for approved_by
        approved_by_info = None
        if approved_by:
            approved_by_info = {
                "user_uid": approved_by.user_uid,
                "name": approved_by.name,
                "user_name": approved_by.user_name,
                "role": approved_by.role
            }

        news_data = {
            "id": news.id,
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary,
            "image_url": news.image_url,
            "category": categories,
            "language": news.language.name if news.language else None,
            "is_approved": news.is_approved,
            "created_at": news.created_at,
            "updated_at": news.updated_at,
            "city": city_name,
            "state": state_name,
            "district": district_name,
            "city": city_name,
            "user_name": posted_by.name if posted_by else None,
            "posted_by": posted_by_info,
            "approved_by": approved_by_info,
        }

        feed.append({"type": "news", "data": news_data})
        news_count += 1  # Increment news counter

        # Inject ads after every 3 news items (after news items 3, 6, 9, etc.)
        if news_count % 3 == 0 and ad_idx < len(ads):
            feed.append({"type": "ad", "data": schemas.AdItem.from_orm(ads[ad_idx]).dict()})
            ad_idx += 1

        # Inject sponsored posts after every 6 news items (after news items 6, 12, 18, etc.)
        if news_count % 6 == 0 and sponsor_idx < len(sponsored_posts):
            feed.append({"type": "sponsored", "data": schemas.SponsoredItem.from_orm(sponsored_posts[sponsor_idx]).dict()})
            sponsor_idx += 1

    return feed
# ADMIN USER CREATION API
# =====================================================

@router.post("/admin/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Admin"])
def create_user_by_admin(
    user_data: schemas.AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new user (Admin only)
    - No OTP verification required
    - Admin can set all user details directly
    - Username max length: 18 characters
    """
    try:
        # Check if phone already exists
        if user_data.phone:
            existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
            if existing_phone:
                raise HTTPException(status_code=400, detail="Phone number already registered")
        
        # Check if email already exists
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate and check username
        user_name = user_data.user_name
        
        if user_name:
            # Check username length
            if len(user_name) > 18:
                raise HTTPException(status_code=400, detail="Username must be 18 characters or less")
            
            # Check if username already exists
            existing_username = db.query(User).filter(User.user_name == user_name).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Username already taken")
        else:
            # Generate unique username with max 18 chars
            user_name = generate_unique_username(db)
            # Double-check length
            if len(user_name) > 18:
                user_name = user_name[:18]
        
        # Generate unique user_uid (8 chars)
        user_uid = generate_user_uid(db)
        
        # Create new user
        new_user = User(
            user_uid=user_uid,
            user_name=user_name,
            name=user_data.name,
            phone=user_data.phone,
            email=user_data.email,
            gender=user_data.gender,
            date_of_birth=user_data.date_of_birth,
            language=user_data.language,
            state_id=user_data.state_id,
            district_id=user_data.district_id,
            city_id=user_data.city_id,
            role=user_data.role,
            email_verified=user_data.email_verified if user_data.email_verified is not None else bool(user_data.email),
            mobile_verified=user_data.mobile_verified if user_data.mobile_verified is not None else bool(user_data.phone),
            created_at=datetime.utcnow(),
            token_version=0,
            is_suspended=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # If user has preferences, create them
        if user_data.preferences:
            pref = user_data.preferences
            # Validate language
            language = db.query(Language).filter(Language.id == pref.language_id).first()
            if not language:
                raise HTTPException(status_code=400, detail="Invalid language ID")
            
            # Create preferences
            user_pref = UserPreference(
                user_uid=new_user.user_uid,
                language_id=pref.language_id,
                state_id=pref.state_id,
                district_id=pref.district_id,
                city_id=pref.city_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Add categories if provided
            if pref.category_ids:
                categories = db.query(Category).filter(Category.id.in_(pref.category_ids)).all()
                if len(categories) != len(pref.category_ids):
                    raise HTTPException(status_code=400, detail="Invalid category IDs")
                user_pref.categories = categories
            
            db.add(user_pref)
            db.commit()
        
        # Return user data
        return {
            "user_uid": new_user.user_uid,
            "user_name": new_user.user_name,
            "name": new_user.name,
            "phone": new_user.phone,
            "email": new_user.email,
            "gender": new_user.gender,
            "date_of_birth": new_user.date_of_birth,
            "language": new_user.language,
            "state_id": new_user.state_id,
            "district_id": new_user.district_id,
            "city_id": new_user.city_id,
            "role": new_user.role,
            "email_verified": new_user.email_verified,
            "mobile_verified": new_user.mobile_verified,
            "created_at": new_user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

