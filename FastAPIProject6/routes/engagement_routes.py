from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.dependencies import admin_required
from models.content import Event, Poll
from models.engagement import Bookmark, Notification
from database import get_db
from models.news import News
from models.user import User
from schemas import AdminNotificationRequest, BookmarkCreate, BookmarkOut, NotificationOut

# router = APIRouter()


# @router.get("/bookmarks/item", tags=["Bookmarks"])
# def get_bookmarked_item(user_uid: str, content_type: str, content_id: int, db: Session = Depends(get_db)):
#     bookmark = db.query(Bookmark).filter_by(
#         user_uid=user_uid,
#         content_type=content_type,
#         content_id=content_id
#     ).first()

#     if not bookmark:
#         raise HTTPException(status_code=404, detail="Bookmark not found")

#     if content_type == "news":
#         item = db.query(News).filter_by(id=content_id).first()
#     elif content_type == "event":
#         item = db.query(Event).filter_by(id=content_id).first()
#     elif content_type == "poll":
#         item = db.query(Poll).filter_by(id=content_id).first()
#     else:
#         raise HTTPException(status_code=400, detail="Invalid content type")

#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")

#     return item


# @router.get("/bookmarks/item/details", tags=["Bookmarks"])
# def get_bookmarked_item_details(user_uid: str, content_type: str, content_id: int, db: Session = Depends(get_db)):
#     bookmark = db.query(Bookmark).filter_by(
#         user_uid=user_uid,
#         content_type=content_type,
#         content_id=content_id
#     ).first()

#     if not bookmark:
#         raise HTTPException(status_code=404, detail="Bookmark not found")

#     item = None
#     if content_type == "news":
#         item = db.query(News).filter_by(id=content_id).first()
#     elif content_type == "event":
#         item = db.query(Event).filter_by(id=content_id).first()
#     elif content_type == "poll":
#         item = db.query(Poll).filter_by(id=content_id).first()
#     else:
#         raise HTTPException(status_code=400, detail="Invalid content type")

#     if not item:
#         raise HTTPException(status_code=404, detail="Content not found")

#     return {
#         "bookmark": {
#             "id": bookmark.id,
#             "user_uid": bookmark.user_uid,
#             "content_type": bookmark.content_type,
#             "content_id": bookmark.content_id,
#             "created_at": bookmark.created_at,
#         },
#         "content": item
#     }

# @router.get("/bookmarks/{user_uid}", response_model=List[BookmarkOut], tags=["Bookmarks"])
# def get_user_bookmarks(user_uid: str, db: Session = Depends(get_db)):
#     return db.query(Bookmark).filter(Bookmark.user_uid == user_uid).all()

# @router.delete("/bookmarks", tags=["Bookmarks"])
# def remove_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
#     deleted = db.query(Bookmark).filter_by(
#         user_uid=bookmark.user_uid,
#         content_type=bookmark.content_type,
#         content_id=bookmark.content_id
#     ).delete()
#     db.commit()
    
#     if deleted:
#         return {"message": "Bookmark removed"}
#     raise HTTPException(status_code=404, detail="Bookmark not found")


# @router.get("/notifications/{user_uid}", response_model=List[NotificationOut], tags=["Notifications"])
# def get_notifications_by_user(user_uid: str, db: Session = Depends(get_db)):
#     """
#     Retrieve notifications for a given user_uid, ordered by newest first.
#     """
#     notifications = (
#         db.query(Notification)
#         .filter(Notification.user_uid == user_uid)
#         .order_by(Notification.created_at.desc())
#         .all()
#     )

#     if not notifications:
#         # Optional: you can return an empty list or raise 404
#         # return []
#         raise HTTPException(status_code=404, detail="No notifications found for this user")
    
#     return notifications


# @router.post("/admin/send", response_model=dict)
# def send_admin_notification(
#     data: AdminNotificationRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(admin_required),  # Only admins allowed
# ):
#     query = db.query(User)

#     # Filter users based on target
#     if data.target_type == "all":
#         users = query.all()
#     elif data.target_type == "state":
#         users = query.filter(User.state == data.target_value).all()
#     elif data.target_type == "district":
#         users = query.filter(User.district == data.target_value).all()
#     elif data.target_type == "city":
#         users = query.filter(User.city == data.target_value).all()
#     elif data.target_type == "user":
#         users = query.filter(User.user_uid == data.target_value).all()
#     else:
#         raise HTTPException(status_code=400, detail="Invalid target_type")

#     if not users:
#         return {"status": "No users found for target"}

#     for user in users:
#         notification = Notification(
#             user_uid=user.user_uid,
#             title=data.title,
#             message=data.message,
#             link_url=data.link_url,
#             notification_type="custom"
#         )
#         db.add(notification)

#     db.commit()
#     return {"status": f"Sent to {len(users)} user(s)"}
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from auth.dependencies import admin_required
from database import get_db

from models.content import Event, Poll
from models.engagement import Bookmark, Notification
from models.news import News
from models.user import User

from schemas import (
    AdminNotificationRequest,
    BookmarkCreate,
    BookmarkOut,
    NotificationOut
)

router = APIRouter()

# =========================================================
# BOOKMARKS
# =========================================================

@router.get("/bookmarks/{user_uid}", response_model=List[BookmarkOut], tags=["Bookmarks"])
def get_user_bookmarks(user_uid: str, db: Session = Depends(get_db)):
    """
    Get all bookmarks for a user
    """
    bookmarks = db.query(Bookmark).filter(Bookmark.user_uid == user_uid).all()
    return bookmarks


# ---------------------------------------------------------

@router.get("/bookmarks/item", tags=["Bookmarks"])
def get_bookmarked_item(
    user_uid: str,
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    """
    Get bookmarked content with details
    """

    bookmark = db.query(Bookmark).filter_by(
        user_uid=user_uid,
        content_type=content_type,
        content_id=content_id
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if content_type == "news":
        item = db.query(News).filter(News.id == content_id).first()

    elif content_type == "event":
        item = db.query(Event).filter(Event.id == content_id).first()

    elif content_type == "poll":
        item = db.query(Poll).filter(Poll.id == content_id).first()

    else:
        raise HTTPException(status_code=400, detail="Invalid content type")

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    return {
        "bookmark": bookmark,
        "content": item
    }


# ---------------------------------------------------------

@router.delete("/bookmarks", tags=["Bookmarks"])
def remove_bookmark(
    bookmark: BookmarkCreate,
    db: Session = Depends(get_db)
):
    """
    Remove a bookmark
    """

    existing = db.query(Bookmark).filter_by(
        user_uid=bookmark.user_uid,
        content_type=bookmark.content_type,
        content_id=bookmark.content_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(existing)
    db.commit()

    return {"message": "Bookmark removed successfully"}


# =========================================================
# NOTIFICATIONS
# =========================================================

@router.get(
    "/notifications/{user_uid}",
    response_model=List[NotificationOut],
    tags=["Notifications"]
)
def get_notifications_by_user(
    user_uid: str,
    limit: int = Query(50, description="Number of notifications"),
    db: Session = Depends(get_db)
):
    """
    Retrieve notifications for a user
    """

    notifications = (
        db.query(Notification)
        .filter(Notification.user_uid == user_uid)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )

    return notifications


# =========================================================
# ADMIN NOTIFICATION
# =========================================================

@router.post("/admin/send", response_model=dict, tags=["Admin Notifications"])
def send_admin_notification(
    data: AdminNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    Send custom notification to users
    """

    query = db.query(User)

    if data.target_type == "all":
        users = query.all()

    elif data.target_type == "state":
        users = query.filter(User.state_id == data.target_value).all()

    elif data.target_type == "district":
        users = query.filter(User.district_id == data.target_value).all()

    elif data.target_type == "city":
        users = query.filter(User.city_id == data.target_value).all()

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

    return {
        "status": "success",
        "sent_to": len(users)
    }