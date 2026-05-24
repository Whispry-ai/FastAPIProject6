from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from models.engagement import Notification

from datetime import datetime, timedelta
from database import SessionLocal
import models  # ✅ import the models module itself

# ============================================================
# 🧹 CLEANUP JOBS DEFINITIONS
# ============================================================

def delete_old_rejected_news():
    """Delete news rejected for more than 2 hours."""
    db: Session = SessionLocal()
    try:
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        old_news = db.query(models.News).filter(
            models.News.is_approved == 2,
            models.News.rejected_at != None,
            models.News.rejected_at <= two_hours_ago
        )
        count = old_news.count()
        old_news.delete(synchronize_session=False)
        db.commit()
        if count:
            print(f"🗑️ Deleted {count} rejected news items older than 2 hours.")
    except Exception as e:
        print("❌ Error deleting rejected news:", e)
    finally:
        db.close()


def delete_expired_sponsored_posts():
    """Delete sponsored posts whose end date has passed."""
    db: Session = SessionLocal()
    try:
        expired = db.query(models.SponsoredPost).filter(
            models.SponsoredPost.end_date < datetime.utcnow()
        )
        count = expired.count()
        expired.delete(synchronize_session=False)
        db.commit()
        if count:
            print(f"💸 Deleted {count} expired sponsored posts.")
    except Exception as e:
        print("❌ Error deleting expired sponsored posts:", e)
    finally:
        db.close()


def deactivate_expired_ads():
    """Deactivate ads whose end date has passed."""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        expired_ads = db.query(models.Advertisement).filter(
            models.Advertisement.end_date <= now,
            models.Advertisement.is_active == True
        )
        count = expired_ads.count()
        for ad in expired_ads:
            ad.is_active = False
        db.commit()
        if count:
            print(f"📢 Deactivated {count} expired ads.")
    except Exception as e:
        print("❌ Error deactivating ads:", e)
    finally:
        db.close()


def delete_expired_polls():
    """Delete polls whose expiration date has passed."""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        expired = db.query(models.Poll).filter(
            models.Poll.expires_at != None,
            models.Poll.expires_at <= now
        )
        count = expired.count()
        expired.delete(synchronize_session=False)
        db.commit()
        if count:
            print(f"🗳️ Deleted {count} expired polls.")
    except Exception as e:
        print("❌ Error deleting expired polls:", e)
    finally:
        db.close()


def delete_old_unread_notifications():
    """Delete unread notifications older than 5 minutes."""
    db: Session = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        deleted = db.query(models.Notification).filter(
            models.Notification.created_at < cutoff_time,
            models.Notification.is_read == False
        ).delete()
        db.commit()
        if deleted:
            print(f"🔔 Deleted {deleted} unread notifications older than 5 minutes.")
    except Exception as e:
        print("❌ Error deleting unread notifications:", e)
    finally:
        db.close()


# ============================================================
# 🕒 SCHEDULER CONFIGURATION
# ============================================================

scheduler = BackgroundScheduler()

# Add all cleanup jobs
scheduler.add_job(delete_old_rejected_news, "interval", minutes=10)
scheduler.add_job(delete_expired_sponsored_posts, "interval", hours=1)
scheduler.add_job(deactivate_expired_ads, "interval", hours=1)
scheduler.add_job(delete_expired_polls, "interval", hours=1)
scheduler.add_job(delete_old_unread_notifications, "interval", minutes=1)

scheduler.start()
print("✅ Scheduler started successfully with all cleanup jobs.")


# ============================================================
# 🧠 Optional external trigger
# ============================================================

def start_notification_cleaner():
    """Kept for backward compatibility (no need to call manually)."""
    print("ℹ️ Notification cleaner already active via main scheduler.")
