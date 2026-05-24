# from datetime import datetime, timedelta
# import random
# from typing import List, Optional

# # from charset_normalizer import models
# from fastapi import APIRouter, Depends, HTTPException, Query,status
# from fastapi import APIRouter, Depends, HTTPException

# from grpc import Status
# import jwt
# from sqlalchemy.orm import Session
# from sqlalchemy import or_
# from datetime import datetime, timedelta
# import random

# from database import get_db
# from models.base_location import Language
# from utility import generate_otp, generate_user_uid, generate_username, generate_unique_username
# from auth.jwt_handler import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES, \
#     REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY, ALGORITHM, pwd_context
# from auth.dependencies import get_current_user
# import schemas

# from models.user import User, OTPStore, UserPreference
# from models.news import News
# from models.engagement import Notification

# =============================
# Standard Library
# =============================
from datetime import datetime, timedelta
from operator import and_
import random
from sre_parse import State
from typing import List, Optional
from unittest import case

# =============================
# FastAPI
# =============================
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse

# =============================
# Database
# =============================
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

# =============================
# Auth / JWT
# =============================
from jose import jwt
from auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    ALGORITHM,
    pwd_context
)
from auth.dependencies import admin_required, get_current_user, require_role
from auth.google_oauth import oauth

# =============================
# Project Utilities
# =============================
from database import get_db
from utility import (
    generate_otp,
    generate_user_uid,
    generate_username,
    generate_unique_username
)

import schemas

# =============================
# Models
# =============================
from models.user import User, OTPStore, UserPreference
from models.news import News, Category
# from models.category import Category
from models.engagement import Notification
from models.base_location import City, District, Language

router = APIRouter()




# @router.post("/auth/switch-to-publisher")
# def switch_to_publisher(user_uid: str, db: Session = Depends(get_db)):
#     # Step 1: Get user
#     user = db.query(User).filter(User.user_uid == user_uid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.role == schemas.UserRole.PUBLISHER:
#         return {"message": "User is already a publisher", "role": user.role}

#     # Step 2: Collect missing verifications
#     pending = []

#     if not user.email_verified:
#         pending.append("email verification")
#     if not user.mobile_verified:
#         pending.append("mobile verification")
#     if not user.name:
#         pending.append("full name")
#     if not user.date_of_birth:
#         pending.append("date of birth")
#     if not user.gender:
#         pending.append("gender")

#     if pending:
#         return {
#             "message": "Cannot assign publisher role. Please complete missing fields.",
#             "pending_fields": pending,
#             "can_switch": False
#         }

#     # Step 3: Assign role
#     user.role = schemas.UserRole.PUBLISHER
#     db.commit()

#     return {
#         "message": "Successfully switched to publisher",
#         "role": user.role,
#         "can_switch": True
#     }


@router.post("/auth/switch-to-publisher", tags=["Auth"])
def switch_to_publisher(
    user_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Switch to publisher role (self or admin)"""
    
    # Authorization
    if current_user.user_uid != user_uid and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.PUBLISHER:
        return {
            "message": "Already a publisher",
            "user_uid": user.user_uid,
            "can_switch": False
        }
    
    # Check required fields
    missing_fields = []
    if not user.email_verified:
        missing_fields.append("email_verified")
    if not user.mobile_verified:
        missing_fields.append("mobile_verified")
    if not user.user_name:
        missing_fields.append("username")
    if not user.name:
        missing_fields.append("full_name")
    if not user.date_of_birth:
        missing_fields.append("date_of_birth")
    if not user.gender:
        missing_fields.append("gender")
    
    if missing_fields:
        return {
            "message": "Complete missing fields to become publisher",
            "missing_fields": missing_fields,
            "can_switch": False
        }
    
    # Switch role
    user.role = UserRole.PUBLISHER
    user.token_version += 1  # Invalidate old tokens
    db.commit()
    
    return {
        "message": "Successfully switched to publisher",
        "user_uid": user.user_uid,
        "new_role": "publisher",
        "can_switch": True
    }

#-------------------------------------------------------------------------------------------------TOKEN VERIFY LOGIN---------




@router.post("/token/verify/login", response_model=schemas.TokenResponse, tags=["Auth"])
def admin_login(payload: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    # Find user by email or phone
    user = db.query(User).filter(
        (User.email == payload.identifier) | (User.phone == payload.identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User not found for {payload.identifier}")

    # Temporarily bypass role check for testing
    # if str(user.role) != str(payload.role):
    #     raise HTTPException(status_code=403, detail="Role mismatch")

    # Token payload
    token_data = {"sub": str(user.user_uid), "role": user.role}

    # Generate tokens (include token_version)
    access_token = create_access_token(data=token_data, token_version=user.token_version)
    refresh_token = create_refresh_token(data=token_data)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        email=user.email or user.phone
    )


@router.post("/auth/refresh", response_model=schemas.TokenResponse, tags=["Auth"])
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_uid: str = payload.get("sub")
        if not user_uid:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Ensure user exists
        user = db.query(User).filter(User.user_uid == user_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token_data = {"sub": str(user.user_uid), "role": user.role}
        new_access_token = create_access_token(data=token_data, token_version=user.token_version)

        return schemas.TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,  # keep same refresh token
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            email=user.email or user.phone
        )

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/auth/logout", tags=["Auth"])
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Increment token_version to revoke old tokens
    current_user.token_version += 1
    db.commit()
    return {"message": "Successfully logged out. All old tokens are now invalid."}


# =============================
# User
# =============================
# OTP
# =============================
@router.get("/auth/google/login", tags=["Auth"])
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", tags=["Auth"])
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")

        email = user_info.get("email")
        name = user_info.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            # TEMP: Generate username with MAX 10 chars (until DB is updated)
            MAX_USERNAME_LEN = 10  # TEMPORARY - change back to 18 after DB update
            
            # Clean the name
            base_username = name.lower().replace(" ", "_") if name else email.split('@')[0]
            base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')
            
            # Truncate base to fit with suffix
            max_base_len = MAX_USERNAME_LEN - 5
            if len(base_username) > max_base_len:
                base_username = base_username[:max_base_len]
            
            username = base_username
            counter = 1
            
            while db.query(User).filter(User.user_name == username).first():
                suffix = random.randint(1000, 9999)
                username = f"{base_username}_{suffix}"
                if len(username) > MAX_USERNAME_LEN:
                    # Remove from base
                    available = MAX_USERNAME_LEN - len(f"_{suffix}")
                    if available > 0:
                        base_username = base_username[:available]
                        username = f"{base_username}_{suffix}"
                    else:
                        username = f"u{suffix}"[:MAX_USERNAME_LEN]
                
                counter += 1
                if counter > 20:
                    import time
                    username = f"u{int(time.time())}"[:MAX_USERNAME_LEN]
                    break
            
            if len(username) > MAX_USERNAME_LEN:
                username = username[:MAX_USERNAME_LEN]
            
            user_uid = generate_user_uid(db)
            
            user = User(
                user_uid=user_uid,
                user_name=username,
                name=name,
                email=email,
                role=schemas.UserRole.USER.value,
                email_verified=True,
                token_version=0,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token_data = {"sub": str(user.user_uid), "role": user.role}
        access_token = create_access_token(data=token_data, token_version=user.token_version)
        refresh_token = create_refresh_token(data=token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_uid": user.user_uid,
            "user_name": user.user_name,
            "email": user.email
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Google login failed: {str(e)}")


@router.post("/auth/send-otp", tags=["Auth"])
def send_otp(request: schemas.SendOtpRequest, db: Session = Depends(get_db)):
    """
    Sends OTP to the user's provided contact (email/phone).
    """
    # Validate input
    if request.type not in ["email", "mobile"]:
        raise HTTPException(status_code=400, detail="Type must be 'email' or 'mobile'")
    
    if not request.value:
        raise HTTPException(status_code=400, detail="Value cannot be empty")
    
    # Generate 4-digit OTP
    otp_code = generate_otp()  # Default 4 digits
    hashed_otp = pwd_context.hash(otp_code)
    
    # Clean up old unverified OTPs
    db.query(OTPStore).filter(
        OTPStore.type == request.type,
        OTPStore.value == request.value,
        OTPStore.verified == False
    ).delete()
    
    # Store new OTP
    new_otp = OTPStore(
        type=request.type,
        value=request.value,
        otp=hashed_otp,
        verified=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    
    db.add(new_otp)
    db.commit()
    
    return {
        "message": f"OTP sent successfully to {request.value}",
        "otp": otp_code,  # 6-digit OTP
        "expires_in": 300,
        "type": request.type
    }

#-------------------------------------------------------------------------------------------------USER VERIFY OTP------------------

@router.post("/auth/verify-otp", tags=["Auth"])
def verify_otp(payload: schemas.VerifyOtp, db: Session = Depends(get_db)):
    """
    Verify OTP and login/register user
    """
    # Find valid OTP entries
    otp_entries = db.query(OTPStore).filter(
        OTPStore.type == payload.type,
        OTPStore.value == payload.value,
        OTPStore.expires_at >= datetime.utcnow(),
        OTPStore.verified == False
    ).all()
    
    # Verify OTP using bcrypt
    matched_entry = None
    for entry in otp_entries:
        if pwd_context.verify(payload.otp, entry.otp):
            matched_entry = entry
            break
    
    if not matched_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Mark OTP as verified
    matched_entry.verified = True
    db.commit()
    
    # Check if user already exists
    existing_user = None
    if payload.type == "mobile":
        existing_user = db.query(User).filter(User.phone == payload.value).first()
    else:
        existing_user = db.query(User).filter(User.email == payload.value).first()
    
    is_new_user = False
    
    if not existing_user:
        # Create new user
        user_uid = generate_user_uid(db)
        user_name = generate_unique_username(db)
        
        # ✅ FIX: Convert enum to integer value
        new_user = User(
            user_uid=user_uid,
            user_name=user_name,
            phone=payload.value if payload.type == "mobile" else None,
            email=payload.value if payload.type == "email" else None,
            role=schemas.UserRole.USER.value,  # ✅ Use .value to get integer
            mobile_verified=True if payload.type == "mobile" else False,
            email_verified=True if payload.type == "email" else False,
            created_at=datetime.utcnow(),
            token_version=0
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_uid = new_user.user_uid
        is_new_user = True
    else:
        # Update existing user verification status
        if payload.type == "mobile":
            if not existing_user.phone:
                existing_user.phone = payload.value
            existing_user.mobile_verified = True
        else:
            if not existing_user.email:
                existing_user.email = payload.value
            existing_user.email_verified = True
        db.commit()
        user_uid = existing_user.user_uid
    
    # Get the final user object
    user = db.query(User).filter(User.user_uid == user_uid).first()
    
    # Generate tokens
    token_data = {"sub": str(user.user_uid), "role": user.role}
    access_token = create_access_token(data=token_data, token_version=user.token_version)
    refresh_token = create_refresh_token(data=token_data)
    
    return {
        "message": "OTP verified successfully",
        "user_uid": user_uid,
        "is_new_user": is_new_user,
        "is_verified": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }



#------------------------------------------------------------------------------------------------------
# =====================================================
# DASHBOARD API - PRODUCTION READY
# =====================================================

@router.get("/dashboard", tags=["User"])
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user dashboard overview with statistics and quick actions.
    
    Returns:
        - User profile information
        - Post statistics (total, approved, pending, rejected)
        - Engagement metrics (views, likes, comments, shares)
        - Recent activity (posts in last 7 days)
        - Last 5 posts preview
        - Quick actions based on user status
    """
    user_uid = current_user.user_uid
    
    # 1️⃣ Get user with basic info
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2️⃣ Get post counts (separate queries for clarity and performance)
    total_posts = db.query(News).filter(News.user_uid == user_uid).count()
    approved = db.query(News).filter(News.user_uid == user_uid, News.is_approved == 1).count()
    pending = db.query(News).filter(
        News.user_uid == user_uid,
        News.is_approved == 0,
        News.rejected_at == None
    ).count()
    rejected = db.query(News).filter(
        News.user_uid == user_uid,
        News.rejected_at != None
    ).count()
    
    # 3️⃣ Get engagement totals
    total_views = db.query(func.sum(News.views_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_likes = db.query(func.sum(News.likes_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_comments = db.query(func.sum(News.comments_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_shares = db.query(func.sum(News.shares_count)).filter(News.user_uid == user_uid).scalar() or 0
    
    # 4️⃣ Calculate engagement rate
    total_interactions = total_likes + total_comments + total_shares
    engagement_rate = round(total_interactions / total_views * 100, 2) if total_views > 0 else 0
    
    # 5️⃣ Get recent activity (posts in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(News).filter(
        News.user_uid == user_uid,
        News.created_at >= week_ago
    ).count()
    
    # 6️⃣ Get recent posts for preview (limit 5)
    recent_posts = db.query(News).filter(
        News.user_uid == user_uid
    ).order_by(desc(News.created_at)).limit(5).all()
    
    # 7️⃣ Build response
    return {
        "user": {
            "user_uid": user.user_uid,
            "user_name": user.user_name,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "role_name": _get_role_name(user.role),
            "is_publisher": user.role == 2,
            "is_verified": user.email_verified and user.mobile_verified,
            "member_since": user.created_at,
            "profile_completion": _calculate_profile_completion(user)
        },
        "statistics": {
            "posts": {
                "total": total_posts,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
                "approval_rate": round(approved / total_posts * 100, 2) if total_posts > 0 else 0
            },
            "engagement": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_views_per_post": round(total_views / total_posts, 2) if total_posts > 0 else 0,
                "engagement_rate": engagement_rate
            }
        },
        "recent_activity": {
            "posts_last_7_days": recent_activity,
            "has_activity": recent_activity > 0
        },
        "recent_posts": [
            {
                "news_uid": p.news_uid,
                "title": p.title,
                "summary": p.summary[:150] if p.summary else None,
                "created_at": p.created_at,
                "status": _get_post_status(p),
                "views": p.views_count,
                "likes": p.likes_count
            }
            for p in recent_posts
        ],
        "quick_actions": _get_quick_actions(user)
    }


# =====================================================
# HELPER FUNCTIONS
# =====================================================

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


def _calculate_profile_completion(user: User) -> int:
    """Calculate profile completion percentage"""
    fields = [
        user.user_name,
        user.name,
        user.email,
        user.phone,
        user.gender,
        user.date_of_birth,
        user.language,
        user.state_id,
        user.district_id,
        user.city_id
    ]
    completed = sum(1 for f in fields if f)
    return int((completed / len(fields)) * 100)


def _get_post_status(news) -> str:
    """Get human-readable post status"""
    if news.is_approved == 1:
        return "approved"
    elif news.rejected_at:
        return "rejected"
    else:
        return "pending"


def _get_quick_actions(user: User) -> list:
    """Get quick actions based on user role and profile completion"""
    actions = [
        {"label": "Create News", "url": "/news/create", "icon": "plus", "type": "primary"}
    ]
    
    if user.role == 2:  # PUBLISHER
        actions.append({"label": "View Analytics", "url": "/analytics", "icon": "chart", "type": "secondary"})
    
    if not user.email_verified:
        actions.append({"label": "Verify Email", "url": "/verify-email", "icon": "mail", "type": "warning"})
    
    if not user.mobile_verified:
        actions.append({"label": "Verify Mobile", "url": "/verify-mobile", "icon": "phone", "type": "warning"})
    
    if _calculate_profile_completion(user) < 80:
        actions.append({"label": "Complete Profile", "url": "/profile/edit", "icon": "user", "type": "info"})
    
    return actions
@router.get("/dashboard/posts", tags=["User"])
def get_user_posts(
    status: str = Query("all", enum=["all", "approved", "pending", "rejected"]),
    sort_by: str = Query("created_at", enum=["created_at", "views", "likes", "comments", "shares"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, min_length=2, description="Search by title"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get paginated list of user's posts.
    Use this for "View All Posts" pages.
    
    - **status**: Filter by post status (all, approved, pending, rejected)
    - **sort_by**: Sort by field (created_at, views, likes, comments, shares)
    - **sort_order**: asc or desc
    - **page**: Page number (starts at 1)
    - **limit**: Items per page (max 100)
    - **search**: Search by title (optional)
    - **date_from**: Filter posts created after this date
    - **date_to**: Filter posts created before this date
    """
    user_uid = current_user.user_uid
    
    # Build base query
    query = db.query(News).filter(News.user_uid == user_uid)
    
    # Apply status filter
    if status == "approved":
        query = query.filter(News.is_approved == 1)
    elif status == "pending":
        query = query.filter(News.is_approved == 0, News.rejected_at == None)
    elif status == "rejected":
        query = query.filter(News.rejected_at != None)
    
    # Apply search filter
    if search:
        query = query.filter(News.title.ilike(f"%{search}%"))
    
    # Apply date filters
    if date_from:
        query = query.filter(News.created_at >= date_from)
    if date_to:
        query = query.filter(News.created_at <= date_to)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(News, sort_by, News.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    offset = (page - 1) * limit
    posts = query.offset(offset).limit(limit).all()
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    
    return {
        "metadata": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "previous_page": page - 1 if page > 1 else None
        },
        "items": [
            {
                "news_uid": p.news_uid,
                "title": p.title,
                "summary": p.summary[:200] if p.summary else None,
                "image_url": p.image_url,
                "created_at": p.created_at,
                "status": _get_post_status(p),
                "views": p.views_count,
                "likes": p.likes_count,
                "comments": p.comments_count,
                "shares": p.shares_count,
                "rejection_reason": getattr(p, 'rejection_reason', None) if p.rejected_at else None,
                "can_edit": p.is_approved == 0 and not p.rejected_at,
                "can_delete": True
            }
            for p in posts
        ]
    }

@router.get("/dashboard/engagement", tags=["User"])
def get_dashboard_engagement(
    period: str = Query("week", enum=["day", "week", "month", "year", "all"]),
    metric: str = Query("all", enum=["all", "views", "likes", "comments", "shares"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user engagement analytics with time series data for charts.
    - Shows trends over time
    - Supports different time periods
    - Returns data ready for charting libraries
    """
    user_uid = current_user.user_uid
    now = datetime.utcnow()
    
    # Define time ranges and intervals based on period
    if period == "day":
        start_date = now - timedelta(days=1)
        interval = "hour"
        format_str = "%Y-%m-%d %H:00"
    elif period == "week":
        start_date = now - timedelta(days=7)
        interval = "day"
        format_str = "%Y-%m-%d"
    elif period == "month":
        start_date = now - timedelta(days=30)
        interval = "day"
        format_str = "%Y-%m-%d"
    elif period == "year":
        start_date = now - timedelta(days=365)
        interval = "week"
        format_str = "%Y-%W"  # Year-Week format
    else:  # all
        start_date = datetime(2000, 1, 1)
        interval = "month"
        format_str = "%Y-%m"
    
    # Get time series data based on period
    if period == "day":
        # Hourly breakdown for last 24 hours
        time_series = []
        for hour in range(24):
            hour_start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            views = db.query(func.sum(News.views_count)).filter(
                News.user_uid == user_uid,
                News.created_at >= hour_start,
                News.created_at < hour_end
            ).scalar() or 0
            
            likes = db.query(func.sum(News.likes_count)).filter(
                News.user_uid == user_uid,
                News.created_at >= hour_start,
                News.created_at < hour_end
            ).scalar() or 0
            
            comments = db.query(func.sum(News.comments_count)).filter(
                News.user_uid == user_uid,
                News.created_at >= hour_start,
                News.created_at < hour_end
            ).scalar() or 0
            
            shares = db.query(func.sum(News.shares_count)).filter(
                News.user_uid == user_uid,
                News.created_at >= hour_start,
                News.created_at < hour_end
            ).scalar() or 0
            
            time_series.append({
                "period": hour_start.strftime("%H:00"),
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "posts": db.query(News).filter(
                    News.user_uid == user_uid,
                    News.created_at >= hour_start,
                    News.created_at < hour_end
                ).count()
            })
    
    else:
        # Get data grouped by interval (day/week/month)
        time_series = db.query(
            func.date_trunc(interval, News.created_at).label('period'),
            func.count(News.id).label('posts'),
            func.sum(News.views_count).label('views'),
            func.sum(News.likes_count).label('likes'),
            func.sum(News.comments_count).label('comments'),
            func.sum(News.shares_count).label('shares')
        ).filter(
            News.user_uid == user_uid,
            News.created_at >= start_date
        ).group_by('period').order_by('period').all()
        
        time_series = [
            {
                "period": t.period.isoformat() if hasattr(t.period, 'isoformat') else str(t.period),
                "views": t.views or 0,
                "likes": t.likes or 0,
                "comments": t.comments or 0,
                "shares": t.shares or 0,
                "posts": t.posts
            }
            for t in time_series
        ]
    
    # Get overall totals
    totals = db.query(
        func.sum(News.views_count).label('total_views'),
        func.sum(News.likes_count).label('total_likes'),
        func.sum(News.comments_count).label('total_comments'),
        func.sum(News.shares_count).label('total_shares')
    ).filter(News.user_uid == user_uid).first()
    
    total_views = totals.total_views or 0
    total_likes = totals.total_likes or 0
    total_comments = totals.total_comments or 0
    total_shares = totals.total_shares or 0
    
    # Get top posts by engagement
    top_posts = db.query(News).filter(
        News.user_uid == user_uid,
        News.is_approved == 1
    ).order_by(
        desc(News.views_count)
    ).limit(5).all()
    
    # Calculate growth (compare last period vs previous)
    growth = {}
    if len(time_series) >= 2:
        current = time_series[-1]
        previous = time_series[-2]
        
        growth = {
            "views": {
                "current": current["views"],
                "previous": previous["views"],
                "percentage": round((current["views"] - previous["views"]) / previous["views"] * 100, 2) if previous["views"] > 0 else 0,
                "trend": "up" if current["views"] > previous["views"] else "down"
            },
            "likes": {
                "current": current["likes"],
                "previous": previous["likes"],
                "percentage": round((current["likes"] - previous["likes"]) / previous["likes"] * 100, 2) if previous["likes"] > 0 else 0,
                "trend": "up" if current["likes"] > previous["likes"] else "down"
            }
        }
    
    # Filter by metric if specified
    if metric != "all":
        for item in time_series:
            for key in list(item.keys()):
                if key not in ["period", metric]:
                    item[key] = None
    
    return {
        "period": period,
        "time_range": {
            "start": start_date.isoformat(),
            "end": now.isoformat()
        },
        "summary": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_engagement": total_likes + total_comments + total_shares,
            "engagement_rate": round((total_likes + total_comments + total_shares) / total_views * 100, 2) if total_views > 0 else 0
        },
        "time_series": time_series,
        "growth": growth,
        "top_posts": [
            {
                "news_uid": p.news_uid,
                "title": p.title,
                "views": p.views_count,
                "likes": p.likes_count,
                "comments": p.comments_count,
                "shares": p.shares_count,
                "engagement_rate": round(
                    (p.likes_count + p.comments_count + p.shares_count) / p.views_count * 100, 2
                ) if p.views_count > 0 else 0
            }
            for p in top_posts
        ],
        "peak_performance": {
            "best_day": max(time_series, key=lambda x: x["views"])["period"] if time_series else None,
            "best_views": max(time_series, key=lambda x: x["views"])["views"] if time_series else 0
        }
    }
@router.get("/dashboard1", tags=["User"])
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recent_limit: int = Query(5, ge=1, le=20, description="Number of recent posts to show"),
):
    """
    Get user dashboard overview (lightweight, fast).
    For viewing all posts, use /dashboard/posts endpoint.
    """
    user_uid = current_user.user_uid
    
    # Get user
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get counts (fast with indexes)
    total_posts = db.query(News).filter(News.user_uid == user_uid).count()
    approved = db.query(News).filter(News.user_uid == user_uid, News.is_approved == 1).count()
    pending = db.query(News).filter(
        News.user_uid == user_uid,
        News.is_approved == 0,
        News.rejected_at == None
    ).count()
    rejected = db.query(News).filter(
        News.user_uid == user_uid,
        News.rejected_at != None
    ).count()
    
    # Engagement totals (fast with indexes)
    total_views = db.query(func.sum(News.views_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_likes = db.query(func.sum(News.likes_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_comments = db.query(func.sum(News.comments_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_shares = db.query(func.sum(News.shares_count)).filter(News.user_uid == user_uid).scalar() or 0
    
    # Recent activity (posts in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(News).filter(
        News.user_uid == user_uid,
        News.created_at >= week_ago
    ).count()
    
    # Recent posts (limited for performance)
    recent_posts = db.query(News).filter(
        News.user_uid == user_uid
    ).order_by(desc(News.created_at)).limit(recent_limit).all()
    
    # Calculate if user has more posts
    has_more_posts = total_posts > recent_limit
    
    return {
        "user": {
            "user_uid": user.user_uid,
            "user_name": user.user_name,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "role_name": _get_role_name(user.role),
            "is_publisher": user.role == schemas.UserRole.PUBLISHER,
            "is_verified": user.email_verified and user.mobile_verified,
            "member_since": user.created_at,
            "profile_completion": _calculate_profile_completion(user)
        },
        "statistics": {
            "posts": {
                "total": total_posts,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
                "approval_rate": round(approved / total_posts * 100, 2) if total_posts > 0 else 0
            },
            "engagement": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_views_per_post": round(total_views / total_posts, 2) if total_posts > 0 else 0,
                "engagement_rate": round(
                    (total_likes + total_comments + total_shares) / total_views * 100, 2
                ) if total_views > 0 else 0
            }
        },
        "recent_activity": {
            "posts_last_7_days": recent_activity,
            "has_activity": recent_activity > 0
        },
        "recent_posts": {
            "items": [
                {
                    "news_uid": p.news_uid,
                    "title": p.title,
                    "summary": p.summary[:150] if p.summary else None,
                    "created_at": p.created_at,
                    "status": _get_post_status(p),
                    "views": p.views_count,
                    "likes": p.likes_count
                }
                for p in recent_posts
            ],
            "has_more": has_more_posts,
            "view_all_url": f"/dashboard/posts?page=1&limit=20"
        },
        "quick_actions": _get_quick_actions(user)
    }
    
@router.get("/users/me", response_model=schemas.UserProfileOut, tags=["User"])
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile"""
    user = db.query(User).filter(User.user_uid == current_user.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "date_of_birth": user.date_of_birth,
        "language": user.language,
        "state_id": user.state_id,
        "district_id": user.district_id,
        "city_id": user.city_id,
        "role": user.role,
        "email_verified": user.email_verified,
        "mobile_verified": user.mobile_verified,
        "is_suspended": user.is_suspended,
        "created_at": user.created_at,
        "updated_at": user.updated_at if hasattr(user, 'updated_at') else user.created_at
    }
@router.get("/admin/users", response_model=dict, tags=["Admin"])
def get_admin_users_list(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    
    # Search
    search: Optional[str] = Query(None, min_length=2, description="Search by name, email, phone, username"),
    
    # Filters
    role: Optional[int] = Query(None, description="Filter by role (0-4)"),
    is_suspended: Optional[bool] = Query(None, description="Filter by suspension status"),
    is_verified: Optional[bool] = Query(None, description="Filter by email/mobile verification"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    language: Optional[str] = Query(None, description="Filter by language code (en, te, hi)"),
    date_from: Optional[datetime] = Query(None, description="Registered from date"),
    date_to: Optional[datetime] = Query(None, description="Registered to date"),
    
    # Sorting
    sort_by: str = Query("created_at", enum=["created_at", "user_name", "name", "email", "role", "total_posts", "total_views"], description="Sort field"),
    sort_order: str = Query("desc", enum=["asc", "desc"], description="Sort order"),
    
    # Additional options
    include_stats: bool = Query(False, description="Include post statistics for each user"),
    export: bool = Query(False, description="Export as CSV (ignores pagination)"),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Get paginated list of all users with advanced filtering.
    Admin only access.
    
    - **page**: Page number for pagination
    - **limit**: Number of users per page (max 100)
    - **search**: Search across name, email, phone, username
    - **role**: Filter by user role (0:GUEST, 1:USER, 2:PUBLISHER, 3:EMPLOYEE, 4:ADMIN)
    - **is_suspended**: Filter suspended/active users
    - **is_verified**: Filter verified/unverified users
    - **state_id, district_id, city_id**: Location filters
    - **language**: Language code filter
    - **date_from, date_to**: Registration date range
    - **sort_by**: Field to sort by
    - **sort_order**: asc or desc
    - **include_stats**: Include post statistics (total posts, views, etc.)
    - **export**: Export results as CSV file
    """
    
    # Build base query
    query = db.query(User)
    
    # =========================================================
    # APPLY FILTERS
    # =========================================================
    
    # Search filter (multiple fields)
    if search:
        query = query.filter(
            or_(
                User.user_name.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
        )
    
    # Role filter
    if role is not None:
        if role not in [0, 1, 2, 3, 4]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 0-4")
        query = query.filter(User.role == role)
    
    # Suspension filter
    if is_suspended is not None:
        query = query.filter(User.is_suspended == is_suspended)
    
    # Verification filter (email or mobile verified)
    if is_verified is not None:
        if is_verified:
            query = query.filter(
                or_(
                    User.email_verified == True,
                    User.mobile_verified == True
                )
            )
        else:
            query = query.filter(
                and_(
                    User.email_verified == False,
                    User.mobile_verified == False
                )
            )
    
    # Location filters
    if state_id:
        query = query.filter(User.state_id == state_id)
    if district_id:
        query = query.filter(User.district_id == district_id)
    if city_id:
        query = query.filter(User.city_id == city_id)
    
    # Language filter
    if language:
        query = query.filter(User.language == language)
    
    # Date range filters
    if date_from:
        query = query.filter(User.created_at >= date_from)
    if date_to:
        query = query.filter(User.created_at <= date_to)
    
    # =========================================================
    # EXPORT MODE (CSV)
    # =========================================================
    
    if export:
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        # Get all users without pagination
        all_users = query.order_by(User.created_at.desc()).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            "User UID", "Username", "Name", "Email", "Phone", "Role", 
            "Email Verified", "Mobile Verified", "Suspended", "Language",
            "State ID", "District ID", "City ID", "Created At"
        ]
        writer.writerow(headers)
        
        # Write data
        for u in all_users:
            writer.writerow([
                u.user_uid, u.user_name or "", u.name or "", u.email or "", u.phone or "",
                _get_role_name(u.role), u.email_verified, u.mobile_verified, u.is_suspended,
                u.language or "", u.state_id or "", u.district_id or "", u.city_id or "",
                u.created_at.isoformat() if u.created_at else ""
            ])
        
        # Return CSV file
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=users_export_{datetime.utcnow().date()}.csv"}
        )
    
    # =========================================================
    # APPLY SORTING
    # =========================================================
    
    # Default sorting
    if sort_by == "created_at":
        sort_column = User.created_at
    elif sort_by == "user_name":
        sort_column = User.user_name
    elif sort_by == "name":
        sort_column = User.name
    elif sort_by == "email":
        sort_column = User.email
    elif sort_by == "role":
        sort_column = User.role
    elif sort_by == "total_posts":
        # This requires subquery - will handle later
        sort_column = None
    elif sort_by == "total_views":
        sort_column = None
    else:
        sort_column = User.created_at
    
    if sort_column and sort_order == "desc":
        query = query.order_by(desc(sort_column))
    elif sort_column:
        query = query.order_by(sort_column)
    else:
        query = query.order_by(desc(User.created_at))
    
    # =========================================================
    # GET TOTAL COUNT BEFORE PAGINATION
    # =========================================================
    
    total_users = query.count()
    
    # =========================================================
    # APPLY PAGINATION
    # =========================================================
    
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()
    
    # =========================================================
    # GET STATISTICS FOR EACH USER (if requested)
    # =========================================================
    
    user_stats = {}
    if include_stats:
        for user in users:
            total_posts = db.query(News).filter(News.user_uid == user.user_uid).count()
            total_views = db.query(func.sum(News.views_count)).filter(News.user_uid == user.user_uid).scalar() or 0
            total_likes = db.query(func.sum(News.likes_count)).filter(News.user_uid == user.user_uid).scalar() or 0
            approved_posts = db.query(News).filter(
                News.user_uid == user.user_uid,
                News.is_approved == 1
            ).count()
            
            user_stats[user.user_uid] = {
                "total_posts": total_posts,
                "total_views": total_views,
                "total_likes": total_likes,
                "approved_posts": approved_posts,
                "approval_rate": round(approved_posts / total_posts * 100, 2) if total_posts > 0 else 0
            }
    
    # =========================================================
    # BUILD RESPONSE
    # =========================================================
    
    total_pages = (total_users + limit - 1) // limit
    
    return {
        "metadata": {
            "total": total_users,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "previous_page": page - 1 if page > 1 else None
        },
        "filters": {
            "search": search,
            "role": role,
            "is_suspended": is_suspended,
            "is_verified": is_verified,
            "state_id": state_id,
            "district_id": district_id,
            "city_id": city_id,
            "language": language,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        },
        "items": [
            {
                "user_uid": u.user_uid,
                "user_name": u.user_name,
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "gender": u.gender,
                "language": u.language,
                "role": u.role,
                "role_name": _get_role_name(u.role),
                "location": {
                    "state_id": u.state_id,
                    "district_id": u.district_id,
                    "city_id": u.city_id
                },
                "verification": {
                    "email_verified": u.email_verified,
                    "mobile_verified": u.mobile_verified
                },
                "status": {
                    "is_suspended": u.is_suspended,
                    "suspension_reason": u.suspension_reason if u.is_suspended else None,
                    "suspension_until": u.suspension_until if u.is_suspended else None
                },
                "created_at": u.created_at,
                "updated_at": u.updated_at if hasattr(u, 'updated_at') else u.created_at,
                "last_login": u.last_login if hasattr(u, 'last_login') else None,
                "stats": user_stats.get(u.user_uid) if include_stats else None
            }
            for u in users
        ]
    }

@router.put("/users/me", response_model=schemas.UserProfileOut, tags=["User"])
def update_my_profile(
    update_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile"""
    user = db.query(User).filter(User.user_uid == current_user.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if update_data.user_name is not None:
        existing = db.query(User).filter(
            User.user_name == update_data.user_name,
            User.user_uid != user.user_uid
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.user_name = update_data.user_name
    
    if update_data.name is not None:
        user.name = update_data.name
    
    if update_data.gender is not None:
        if update_data.gender not in ["male", "female", "other"]:
            raise HTTPException(status_code=400, detail="Gender must be male, female, or other")
        user.gender = update_data.gender
    
    if update_data.date_of_birth is not None:
        user.date_of_birth = update_data.date_of_birth
    
    if update_data.language is not None:
        user.language = update_data.language
    
    if update_data.state_id is not None:
        if update_data.state_id:
            state = db.query(State).filter(State.id == update_data.state_id).first()
            if not state:
                raise HTTPException(status_code=400, detail="Invalid state ID")
        user.state_id = update_data.state_id
    
    if update_data.district_id is not None:
        if update_data.district_id:
            district = db.query(District).filter(District.id == update_data.district_id).first()
            if not district:
                raise HTTPException(status_code=400, detail="Invalid district ID")
        user.district_id = update_data.district_id
    
    if update_data.city_id is not None:
        if update_data.city_id:
            city = db.query(City).filter(City.id == update_data.city_id).first()
            if not city:
                raise HTTPException(status_code=400, detail="Invalid city ID")
        user.city_id = update_data.city_id
    
    if update_data.email is not None:
        existing = db.query(User).filter(
            User.email == update_data.email,
            User.user_uid != user.user_uid
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = update_data.email
        user.email_verified = False
    
    if update_data.phone is not None:
        existing = db.query(User).filter(
            User.phone == update_data.phone,
            User.user_uid != user.user_uid
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already taken")
        user.phone = update_data.phone
        user.mobile_verified = False
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Return updated profile
    return get_my_profile(db=db, current_user=user)


@router.get("/admin/users_profile/{user_uid}", response_model=dict, tags=["Admin"])
def get_admin_user_details(
    user_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
    include_sensitive: bool = Query(False, description="Include sensitive data like token_version"),
    include_activity: bool = Query(True, description="Include user activity log"),
    include_preferences: bool = Query(True, description="Include user preferences"),
    include_posts: bool = Query(True, description="Include user posts with pagination"),
    post_limit: int = Query(10, ge=1, le=50, description="Number of posts to show"),
    post_page: int = Query(1, ge=1, description="Page number for posts"),
):
    """
    Get complete user details for admin.
    
    - **user_uid**: User UID to fetch
    - **include_sensitive**: Include token_version, IP addresses (admin only)
    - **include_activity**: Include user activity log
    - **include_preferences**: Include user preferences
    - **include_posts**: Include user's posts with pagination
    - **post_limit**: Number of posts per page
    - **post_page**: Page number for posts
    """
    # Get user
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # =========================================================
    # 1. BASIC USER INFORMATION
    # =========================================================
    
    # Get location names
    state_name = None
    district_name = None
    city_name = None
    
    if user.state_id:
        state = db.query(State).filter(State.id == user.state_id).first()
        state_name = state.name if state else None
    if user.district_id:
        district = db.query(District).filter(District.id == user.district_id).first()
        district_name = district.name if district else None
    if user.city_id:
        city = db.query(City).filter(City.id == user.city_id).first()
        city_name = city.name if city else None
    
    response = {
        "user_uid": user.user_uid,
        "user_name": user.user_name,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "date_of_birth": user.date_of_birth,
        "language": user.language,
        "location": {
            "state_id": user.state_id,
            "state_name": state_name,
            "district_id": user.district_id,
            "district_name": district_name,
            "city_id": user.city_id,
            "city_name": city_name
        },
        "role": user.role,
        "role_name": _get_role_name(user.role),
        "verification": {
            "email_verified": user.email_verified,
            "mobile_verified": user.mobile_verified,
            "email_verified_at": None,  # Add if you have this field
            "mobile_verified_at": None   # Add if you have this field
        },
        "account_status": {
            "is_suspended": user.is_suspended,
            "suspension_reason": user.suspension_reason if user.is_suspended else None,
            "suspended_at": user.suspended_at if user.is_suspended else None,
            "suspended_until": user.suspended_until if user.is_suspended else None,
            "suspended_by": user.suspended_by if user.is_suspended else None,
            "suspended_by_name": None  # Will fetch if suspended
        },
        "timestamps": {
            "created_at": user.created_at,
            "updated_at": user.updated_at if hasattr(user, 'updated_at') else user.created_at,
            "last_login": user.last_login if hasattr(user, 'last_login') else None
        }
    }
    
    # Get suspended_by name if user is suspended
    if user.is_suspended and user.suspended_by:
        suspender = db.query(User).filter(User.user_uid == user.suspended_by).first()
        if suspender:
            response["account_status"]["suspended_by_name"] = suspender.user_name or suspender.name
    
    # Add sensitive info if requested
    if include_sensitive:
        response["sensitive"] = {
            "token_version": user.token_version,
            "ip_address": None,  # Add if tracked
            "device_info": None,  # Add if tracked
            "created_ip": None,
            "last_login_ip": None
        }
    
    # =========================================================
    # 2. USER PREFERENCES
    # =========================================================
    
    if include_preferences:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_uid == user_uid
        ).first()
        
        if preferences:
            # Get language details
            language = db.query(Language).filter(Language.id == preferences.language_id).first()
            
            # Get location details
            pref_state_name = None
            pref_district_name = None
            pref_city_name = None
            
            if preferences.state_id:
                state = db.query(State).filter(State.id == preferences.state_id).first()
                pref_state_name = state.name if state else None
            if preferences.district_id:
                district = db.query(District).filter(District.id == preferences.district_id).first()
                pref_district_name = district.name if district else None
            if preferences.city_id:
                city = db.query(City).filter(City.id == preferences.city_id).first()
                pref_city_name = city.name if city else None
            
            response["preferences"] = {
                "language_id": preferences.language_id,
                "language_code": language.code if language else None,
                "language_name": language.name if language else None,
                "location": {
                    "state_id": preferences.state_id,
                    "state_name": pref_state_name,
                    "district_id": preferences.district_id,
                    "district_name": pref_district_name,
                    "city_id": preferences.city_id,
                    "city_name": pref_city_name
                },
                "categories": [
                    {"id": cat.id, "name": cat.name}
                    for cat in preferences.categories
                ] if preferences.categories else [],
                "created_at": preferences.created_at,
                "updated_at": preferences.updated_at
            }
        else:
            response["preferences"] = None
    
    # =========================================================
    # 3. USER STATISTICS
    # =========================================================
    
    # Post statistics
    total_posts = db.query(News).filter(News.user_uid == user_uid).count()
    approved_posts = db.query(News).filter(News.user_uid == user_uid, News.is_approved == 1).count()
    pending_posts = db.query(News).filter(
        News.user_uid == user_uid,
        News.is_approved == 0,
        News.rejected_at == None
    ).count()
    rejected_posts = db.query(News).filter(
        News.user_uid == user_uid,
        News.rejected_at != None
    ).count()
    
    # Engagement totals
    total_views = db.query(func.sum(News.views_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_likes = db.query(func.sum(News.likes_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_comments = db.query(func.sum(News.comments_count)).filter(News.user_uid == user_uid).scalar() or 0
    total_shares = db.query(func.sum(News.shares_count)).filter(News.user_uid == user_uid).scalar() or 0
    
    # Calculate averages
    avg_views = round(total_views / total_posts, 2) if total_posts > 0 else 0
    engagement_rate = round((total_likes + total_comments + total_shares) / total_views * 100, 2) if total_views > 0 else 0
    
    # Get best performing post
    best_post = db.query(News).filter(
        News.user_uid == user_uid,
        News.is_approved == 1
    ).order_by(desc(News.views_count)).first()
    
    response["statistics"] = {
        "posts": {
            "total": total_posts,
            "approved": approved_posts,
            "pending": pending_posts,
            "rejected": rejected_posts,
            "approval_rate": round(approved_posts / total_posts * 100, 2) if total_posts > 0 else 0
        },
        "engagement": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "avg_views_per_post": avg_views,
            "engagement_rate": engagement_rate
        },
        "best_performing_post": {
            "news_uid": best_post.news_uid,
            "title": best_post.title,
            "views": best_post.views_count,
            "likes": best_post.likes_count
        } if best_post else None
    }
    
    # =========================================================
    # 4. USER POSTS (PAGINATED)
    # =========================================================
    
    if include_posts:
        # Build query
        post_query = db.query(News).filter(News.user_uid == user_uid)
        
        # Get total posts count
        total_posts_count = post_query.count()
        
        # Apply pagination
        offset = (post_page - 1) * post_limit
        posts = post_query.order_by(desc(News.created_at)).offset(offset).limit(post_limit).all()
        
        response["posts"] = {
            "metadata": {
                "total": total_posts_count,
                "page": post_page,
                "limit": post_limit,
                "total_pages": (total_posts_count + post_limit - 1) // post_limit,
                "has_next": offset + post_limit < total_posts_count,
                "has_previous": post_page > 1
            },
            "items": [
                {
                    "news_uid": p.news_uid,
                    "title": p.title,
                    "summary": p.summary[:200] if p.summary else None,
                    "image_url": p.image_url,
                    "created_at": p.created_at,
                    "status": _get_post_status(p),
                    "engagement": {
                        "views": p.views_count,
                        "likes": p.likes_count,
                        "comments": p.comments_count,
                        "shares": p.shares_count
                    },
                    "categories": [{"id": c.id, "name": c.name} for c in p.categories] if p.categories else []
                }
                for p in posts
            ]
        }
    
    # =========================================================
    # 5. USER ACTIVITY LOG
    # =========================================================
    
    if include_activity:
        # Get activity log (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Get daily activity counts
        daily_activity = db.query(
            func.date(News.created_at).label('date'),
            func.count(News.id).label('posts'),
            func.sum(News.views_count).label('views'),
            func.sum(News.likes_count).label('likes')
        ).filter(
            News.user_uid == user_uid,
            News.created_at >= thirty_days_ago
        ).group_by(func.date(News.created_at)).order_by(func.date(News.created_at)).all()
        
        response["activity"] = {
            "last_30_days": [
                {
                    "date": a.date.isoformat(),
                    "posts": a.posts,
                    "views": a.views or 0,
                    "likes": a.likes or 0
                }
                for a in daily_activity
            ],
            "total_activity": {
                "posts_last_30_days": sum(a.posts for a in daily_activity),
                "views_last_30_days": sum(a.views or 0 for a in daily_activity),
                "likes_last_30_days": sum(a.likes or 0 for a in daily_activity)
            }
        }
    
    # =========================================================
    # 6. ADDITIONAL METRICS
    # =========================================================
    
    # Get category distribution
    category_distribution = db.query(
        Category.id,
        Category.name,
        func.count(News.id).label('count')
    ).join(News.categories).filter(
        News.user_uid == user_uid,
        News.is_approved == 1
    ).group_by(Category.id).order_by(desc('count')).limit(5).all()
    
    response["category_distribution"] = [
        {"id": c.id, "name": c.name, "count": c.count}
        for c in category_distribution
    ]
    
    # Get time distribution (by hour)
    hour_distribution = db.query(
        func.extract('hour', News.created_at).label('hour'),
        func.count(News.id).label('count')
    ).filter(
        News.user_uid == user_uid,
        News.is_approved == 1
    ).group_by('hour').order_by('hour').all()
    
    response["hour_distribution"] = [
        {"hour": int(h.hour), "posts": h.count}
        for h in hour_distribution
    ]
    
    return response
# =============================
# Preferences
# =============================
@router.post("/preference")
def set_user_preference(payload: schemas.UserPreferenceCreate, db: Session = Depends(get_db)):
    pref = UserPreference(**payload.model_dump())
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


@router.post("/preferences", response_model=schemas.UserPreferenceResponse, tags=["Preferences"])
def upsert_user_preference(pref: schemas.UserPreferenceCreate, db: Session = Depends(get_db)):

    # 1️⃣ Check if user exists
    user = db.query(User).filter(User.user_uid == pref.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Check language
    language = db.query(Language).filter(Language.id == pref.language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    lang_code = language.code.lower()

    # 3️⃣ Language validation rules
    if lang_code == "te":
        if not (pref.state_id and pref.district_id and pref.city_id):
            raise HTTPException(status_code=400, detail="Telugu requires state, district, and city")

    elif lang_code == "hi":
        if not pref.state_id:
            raise HTTPException(status_code=400, detail="Hindi requires state only")
        pref.district_id = None
        pref.city_id = None

    elif lang_code == "en":
        pref.state_id = None
        pref.district_id = None
        pref.city_id = None

    else:
        raise HTTPException(status_code=400, detail="Unsupported language (only te, hi, en allowed)")

    # 4️⃣ Validate categories
    categories = []
    if pref.category_ids:
        categories = db.query(Category).filter(Category.id.in_(pref.category_ids)).all()
        if len(categories) != len(pref.category_ids):
            raise HTTPException(status_code=400, detail="Invalid category IDs")

    # 5️⃣ Check if preference exists
    user_pref = db.query(UserPreference).filter(
        UserPreference.user_uid == pref.user_uid
    ).first()

    if user_pref:
        # Update existing
        user_pref.language_id = pref.language_id
        user_pref.state_id = pref.state_id
        user_pref.district_id = pref.district_id
        user_pref.city_id = pref.city_id
        user_pref.categories = categories
        user_pref.updated_at = datetime.utcnow()

    else:
        # Create new
        user_pref = UserPreference(
            user_uid=pref.user_uid,
            language_id=pref.language_id,
            state_id=pref.state_id,
            district_id=pref.district_id,
            city_id=pref.city_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        user_pref.categories = categories
        db.add(user_pref)

    db.commit()
    db.refresh(user_pref)

    return schemas.UserPreferenceResponse(
        user_uid=user_pref.user_uid,
        language=language.code,
        state_id=user_pref.state_id,
        district_id=user_pref.district_id,
        city_id=user_pref.city_id,
        category_ids=[cat.id for cat in user_pref.categories],
        created_at=user_pref.created_at,
        updated_at=user_pref.updated_at,
    )


@router.get("/preferences/{user_uid}", response_model=schemas.UserPreferenceResponse, tags=["Preferences"])
def get_user_preference(user_uid: str, db: Session = Depends(get_db)):
    """
    Fetch the saved preference for a given user_uid including associated categories.
    """
    # 1. Check if user exists
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Fetch preference (using joinedload if you want to optimize SQL queries for categories)
    user_pref = db.query(UserPreference).filter(UserPreference.user_uid == user_uid).first()
    
    if not user_pref:
        raise HTTPException(status_code=404, detail="Preference not set for this user")

    # 3. Get language info (to return the code 'en', 'te', etc., as per POST response)
    language = db.query(Language).filter(Language.id == user_pref.language_id).first()
    lang_code = language.code if language else None

    # 4. Return response matching the schemas.UserPreferenceResponse used in POST
    return schemas.UserPreferenceResponse(
        user_uid=user_pref.user_uid,
        language=lang_code,
        state_id=user_pref.state_id,
        district_id=user_pref.district_id,
        city_id=user_pref.city_id,
        # Extract category IDs from the relationship
        category_ids=[cat.id for cat in user_pref.categories], 
        created_at=user_pref.created_at,
        updated_at=user_pref.updated_at,
    )

@router.delete("/user/news/{news_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_by_user(news_uid: str, user_uid: str, db: Session = Depends(get_db)):
    news = db.query(News).filter_by(news_uid=news_uid, user_uid=user_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found or unauthorized")
    
    db.delete(news)
    db.commit()
    return {"detail": "Your news has been deleted"}

@router.get("/admin/users/stats", tags=["Admin"])
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),  # ✅ Only ADMIN can access
):
    """Get user statistics for admin dashboard"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    suspended_users = db.query(User).filter(User.is_suspended == True).count()
    
    publishers = db.query(User).filter(User.role == schemas.UserRole.PUBLISHER).count()
    admins = db.query(User).filter(User.role == schemas.UserRole.ADMIN).count()
    employees = db.query(User).filter(User.role == schemas.UserRole.EMPLOYEE).count()
    
    # New users this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = db.query(User).filter(User.created_at >= week_ago).count()
    
    # Verification stats
    email_verified = db.query(User).filter(User.email_verified == True).count()
    mobile_verified = db.query(User).filter(User.mobile_verified == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "publishers": publishers,
        "admins": admins,
        "employees": employees,
        "new_users_7_days": new_users,
        "verification": {
            "email_verified": email_verified,
            "mobile_verified": mobile_verified,
            "email_verification_rate": round(email_verified / total_users * 100, 2) if total_users > 0 else 0,
            "mobile_verification_rate": round(mobile_verified / total_users * 100, 2) if total_users > 0 else 0
        }
    }
@router.get("/users/me/profile", tags=["User"])
def get_my_profile_secure(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.USER)),
):
    """Get current user's profile (secure)"""
    user = db.query(User).filter(User.user_uid == current_user.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user preferences
    preferences = db.query(UserPreference).filter(UserPreference.user_uid == user.user_uid).first()
    
    # Get state, district, city names if IDs exist
    state_name = None
    district_name = None
    city_name = None
    
    if user.state_id:
        state = db.query(State).filter(State.id == user.state_id).first()
        state_name = state.name if state else None
    if user.district_id:
        district = db.query(District).filter(District.id == user.district_id).first()
        district_name = district.name if district else None
    if user.city_id:
        city = db.query(City).filter(City.id == user.city_id).first()
        city_name = city.name if city else None
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "date_of_birth": user.date_of_birth,
        "language": user.language,
        "state": state_name,
        "state_id": user.state_id,
        "district": district_name,
        "district_id": user.district_id,
        "city": city_name,
        "city_id": user.city_id,
        "role": user.role,
        "email_verified": user.email_verified,
        "mobile_verified": user.mobile_verified,
        "created_at": user.created_at,
        "preferences": {
            "language_id": preferences.language_id if preferences else None,
            "state_id": preferences.state_id if preferences else None,
            "district_id": preferences.district_id if preferences else None,
            "city_id": preferences.city_id if preferences else None,
            "category_ids": [cat.id for cat in preferences.categories] if preferences else []
        } if preferences else None
    }

# =====================================================
# USER SUSPENSION APIS
# =====================================================

@router.get("/users/{user_uid}/suspension-status", tags=["Admin", "User"])
def check_user_suspension_status(
    user_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),  # Admin only
):
    """Check suspension status of a user (Admin only)"""
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    days_remaining = None
    if user.is_suspended and user.suspended_until:
        days_remaining = (user.suspended_until - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0
    
    # Get suspender name
    suspender_name = None
    if user.suspended_by:
        suspender = db.query(User).filter(User.user_uid == user.suspended_by).first()
        suspender_name = suspender.user_name or suspender.name if suspender else None
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name or user.name,
        "is_suspended": user.is_suspended,
        "suspension_reason": user.suspension_reason,
        "suspended_at": user.suspended_at,
        "suspended_until": user.suspended_until,
        "suspended_by": user.suspended_by,
        "suspended_by_name": suspender_name,
        "days_remaining": days_remaining,
        "is_active": not user.is_suspended or (user.suspended_until and user.suspended_until < datetime.utcnow())
    }


@router.post("/users/{user_uid}/suspend", tags=["Admin"])
def suspend_user(
    user_uid: str,
    request: schemas.UserSuspendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Suspend a user (Admin only)
    
    - **reason**: Reason for suspension (required)
    - **duration_days**: Number of days to suspend (default: 30, max: 365)
    - **notify_user**: Send notification to user (default: True)
    """
    # Prevent self-suspension
    if current_user.user_uid == user_uid:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")
    
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already suspended
    if user.is_suspended:
        # Check if suspension is still active
        if user.suspended_until and user.suspended_until > datetime.utcnow():
            days_left = (user.suspended_until - datetime.utcnow()).days
            raise HTTPException(
                status_code=400, 
                detail=f"User is already suspended for {days_left} more days. Reason: {user.suspension_reason}"
            )
        else:
            # Suspension expired, we can suspend again
            pass
    
    # Calculate suspension end date
    suspended_until = datetime.utcnow() + timedelta(days=request.duration_days)
    
    # Update user
    user.is_suspended = True
    user.suspension_reason = request.reason
    user.suspended_at = datetime.utcnow()
    user.suspended_until = suspended_until
    user.suspended_by = current_user.user_uid
    user.token_version += 1  # Invalidate all tokens
    
    db.commit()
    db.refresh(user)
    
    # Optional: Send notification to user
    if request.notify_user:
        # Create notification for user
        notification = Notification(
            user_uid=user.user_uid,
            title="Account Suspended",
            message=f"Your account has been suspended for {request.duration_days} days. Reason: {request.reason}",
            notification_type="suspension",
            link_url=None
        )
        db.add(notification)
        db.commit()
    
    # Get suspender name
    suspender_name = current_user.user_name or current_user.name
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name or user.name,
        "is_suspended": True,
        "suspension_reason": request.reason,
        "suspended_until": suspended_until,
        "suspended_by": current_user.user_uid,
        "suspended_by_name": suspender_name,
        "duration_days": request.duration_days,
        "message": f"User suspended successfully until {suspended_until.strftime('%Y-%m-%d %H:%M:%S')}"
    }


@router.post("/users/{user_uid}/activate", tags=["Admin"])
def activate_user(
    user_uid: str,
    request: schemas.UserActivateRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Activate a suspended user (Admin only)
    
    - **reason**: Optional reason for activation
    """
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already active
    if not user.is_suspended:
        raise HTTPException(status_code=400, detail="User is already active")
    
    # Calculate suspension duration
    suspension_duration = None
    if user.suspended_at:
        suspension_duration = (datetime.utcnow() - user.suspended_at).days
    
    # Update user
    user.is_suspended = False
    user.activated_at = datetime.utcnow()
    user.token_version += 1  # Invalidate old tokens
    
    # Optional: Add activation reason
    if request and request.reason:
        user.suspension_reason = f"{user.suspension_reason} [Activated: {request.reason}]"
    
    db.commit()
    db.refresh(user)
    
    # Optional: Send notification to user
    notification = Notification(
        user_uid=user.user_uid,
        title="Account Activated",
        message=f"Your account has been activated after {suspension_duration} days.",
        notification_type="activation",
        link_url=None
    )
    db.add(notification)
    db.commit()
    
    # Get activator name
    activator_name = current_user.user_name or current_user.name
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name or user.name,
        "is_suspended": False,
        "activated_at": user.activated_at,
        "suspension_duration_days": suspension_duration,
        "activated_by": current_user.user_uid,
        "activated_by_name": activator_name,
        "message": f"User activated successfully after {suspension_duration} days of suspension"
    }


@router.post("/users/{user_uid}/extend-suspension", tags=["Admin"])
def extend_user_suspension(
    user_uid: str,
    additional_days: int = Query(..., ge=1, le=365, description="Additional days to extend suspension"),
    reason: Optional[str] = Query(None, description="Reason for extension"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Extend suspension for a user (Admin only)
    """
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is suspended
    if not user.is_suspended:
        raise HTTPException(status_code=400, detail="User is not suspended")
    
    # Extend suspension
    if user.suspended_until:
        new_suspended_until = user.suspended_until + timedelta(days=additional_days)
    else:
        new_suspended_until = datetime.utcnow() + timedelta(days=additional_days)
    
    user.suspended_until = new_suspended_until
    if reason:
        user.suspension_reason = f"{user.suspension_reason} [Extended: {reason}]"
    
    user.token_version += 1  # Invalidate all tokens
    
    db.commit()
    db.refresh(user)
    
    return {
        "user_uid": user.user_uid,
        "user_name": user.user_name or user.name,
        "is_suspended": True,
        "suspension_reason": user.suspension_reason,
        "suspended_until": new_suspended_until,
        "additional_days": additional_days,
        "message": f"Suspension extended by {additional_days} days. New end date: {new_suspended_until.strftime('%Y-%m-%d %H:%M:%S')}"
    }


@router.get("/users/suspended", tags=["Admin"])
def get_suspended_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    include_expired: bool = Query(False, description="Include expired suspensions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Get all suspended users (Admin only)
    """
    query = db.query(User).filter(User.is_suspended == True)
    
    if not include_expired:
        # Only show currently active suspensions
        query = query.filter(User.suspended_until > datetime.utcnow())
    
    total = query.count()
    users = query.order_by(User.suspended_until.asc()).offset(offset).limit(limit).all()
    
    results = []
    for user in users:
        # Get suspender name
        suspender_name = None
        if user.suspended_by:
            suspender = db.query(User).filter(User.user_uid == user.suspended_by).first()
            suspender_name = suspender.user_name or suspender.name if suspender else None
        
        days_remaining = None
        if user.suspended_until:
            days_remaining = (user.suspended_until - datetime.utcnow()).days
            if days_remaining < 0:
                days_remaining = 0
        
        results.append({
            "user_uid": user.user_uid,
            "user_name": user.user_name or user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "suspension_reason": user.suspension_reason,
            "suspended_at": user.suspended_at,
            "suspended_until": user.suspended_until,
            "suspended_by": user.suspended_by,
            "suspended_by_name": suspender_name,
            "days_remaining": days_remaining,
            "is_active_suspension": user.suspended_until > datetime.utcnow() if user.suspended_until else True
        })
    
    return {
        "total": total,
        "items": results,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total
    }


@router.get("/users/me/suspension-status", tags=["User"])
def check_my_suspension_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.USER)),
):
    """
    Check current user's suspension status
    """
    user = db.query(User).filter(User.user_uid == current_user.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    days_remaining = None
    if user.is_suspended and user.suspended_until:
        days_remaining = (user.suspended_until - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0
    
    return {
        "is_suspended": user.is_suspended,
        "suspension_reason": user.suspension_reason if user.is_suspended else None,
        "suspended_at": user.suspended_at if user.is_suspended else None,
        "suspended_until": user.suspended_until if user.is_suspended else None,
        "days_remaining": days_remaining if user.is_suspended else None,
        "is_active": not user.is_suspended or (user.suspended_until and user.suspended_until < datetime.utcnow())
    }


# =====================================================
# BULK SUSPENSION APIS
# =====================================================

@router.post("/admin/users/bulk-suspend", tags=["Admin"])
def bulk_suspend_users(
    user_uids: List[str] = Query(..., description="List of user UIDs to suspend"),
    reason: str = Query(..., min_length=5, max_length=500, description="Reason for suspension"),
    duration_days: int = Query(30, ge=1, le=365, description="Suspension duration in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Bulk suspend multiple users (Admin only)
    """
    results = {
        "successful": [],
        "failed": [],
        "total": len(user_uids)
    }
    
    suspended_until = datetime.utcnow() + timedelta(days=duration_days)
    
    for user_uid in user_uids:
        try:
            # Skip self
            if current_user.user_uid == user_uid:
                results["failed"].append({"user_uid": user_uid, "reason": "Cannot suspend yourself"})
                continue
            
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if not user:
                results["failed"].append({"user_uid": user_uid, "reason": "User not found"})
                continue
            
            if user.is_suspended:
                results["failed"].append({"user_uid": user_uid, "reason": "Already suspended"})
                continue
            
            # Suspend user
            user.is_suspended = True
            user.suspension_reason = reason
            user.suspended_at = datetime.utcnow()
            user.suspended_until = suspended_until
            user.suspended_by = current_user.user_uid
            user.token_version += 1
            
            results["successful"].append({
                "user_uid": user_uid,
                "user_name": user.user_name or user.name
            })
            
        except Exception as e:
            results["failed"].append({"user_uid": user_uid, "reason": str(e)})
    
    db.commit()
    
    return {
        "message": f"Bulk suspension completed",
        "successful_count": len(results["successful"]),
        "failed_count": len(results["failed"]),
        "results": results
    }


@router.post("/admin/users/bulk-activate", tags=["Admin"])
def bulk_activate_users(
    user_uids: List[str] = Query(..., description="List of user UIDs to activate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.ADMIN)),
):
    """
    Bulk activate multiple suspended users (Admin only)
    """
    results = {
        "successful": [],
        "failed": [],
        "total": len(user_uids)
    }
    
    for user_uid in user_uids:
        try:
            user = db.query(User).filter(User.user_uid == user_uid).first()
            if not user:
                results["failed"].append({"user_uid": user_uid, "reason": "User not found"})
                continue
            
            if not user.is_suspended:
                results["failed"].append({"user_uid": user_uid, "reason": "User is not suspended"})
                continue
            
            # Activate user
            user.is_suspended = False
            user.activated_at = datetime.utcnow()
            user.token_version += 1
            
            results["successful"].append({
                "user_uid": user_uid,
                "user_name": user.user_name or user.name
            })
            
        except Exception as e:
            results["failed"].append({"user_uid": user_uid, "reason": str(e)})
    
    db.commit()
    
    return {
        "message": f"Bulk activation completed",
        "successful_count": len(results["successful"]),
        "failed_count": len(results["failed"]),
        "results": results
    }