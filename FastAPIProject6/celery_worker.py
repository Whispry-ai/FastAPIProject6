from celery import Celery
from database import SessionLocal
from models.user import User
from models.engagement import Notification

# Celery configuration
celery = Celery(
    "news_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


# ============================
# Notification Task
# ============================

@celery.task(name="send_news_notification")
def send_news_notification(news_uid, title):

    db = SessionLocal()

    try:
        users = db.query(User.user_uid).all()

        notifications = [
            Notification(
                user_uid=user.user_uid,
                title=title,
                message=f"📰 New Update: {title}",
                link_url=f"/news/{news_uid}",
                notification_type="news"
            )
            for user in users
        ]

        db.add_all(notifications)
        db.commit()

    finally:
        db.close()