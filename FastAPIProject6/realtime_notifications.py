"""
Real-time Notification System for Hyperlocal News Application
Handles push notifications, email notifications, and in-app alerts
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from dataclasses import dataclass

from database import SessionLocal
from models.user import User, UserPreference
from models.engagement import Notification
from models.news import News
from websocket_manager import manager

logger = logging.getLogger(__name__)

@dataclass
class NotificationData:
    """Data structure for notifications"""
    title: str
    message: str
    notification_type: str
    target_users: List[str]
    location_filter: Optional[Dict] = None
    priority: str = "normal"
    link_url: Optional[str] = None
    data: Optional[Dict] = None

class RealTimeNotificationService:
    """Service for handling real-time notifications"""
    
    def __init__(self):
        self.active_notifications: Dict[str, datetime] = {}
        self.notification_queue = asyncio.Queue()
        self.is_running = False
    
    async def start(self):
        """Start the notification service"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self.process_notifications())
        logger.info("Real-time notification service started")
    
    async def stop(self):
        """Stop the notification service"""
        self.is_running = False
        logger.info("Real-time notification service stopped")
    
    async def process_notifications(self):
        """Process notifications from queue"""
        while self.is_running:
            try:
                notification_data = await asyncio.wait_for(
                    self.notification_queue.get(), timeout=1.0
                )
                await self.send_notification(notification_data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
    
    async def queue_notification(self, notification_data: NotificationData):
        """Queue a notification for processing"""
        await self.notification_queue.put(notification_data)
    
    async def send_notification(self, notification_data: NotificationData):
        """Send notification through multiple channels"""
        try:
            with SessionLocal() as db:
                # Get target users based on filters
                target_users = self.get_target_users(
                    db, notification_data.target_users, notification_data.location_filter
                )
                
                # Send real-time WebSocket notifications
                await self.send_websocket_notifications(
                    target_users, notification_data
                )
                
                # Store in-app notifications
                await self.store_in_app_notifications(
                    db, target_users, notification_data
                )
                
                # Send push notifications (if enabled)
                await self.send_push_notifications(
                    target_users, notification_data
                )
                
                # Send email notifications (if enabled)
                await self.send_email_notifications(
                    db, target_users, notification_data
                )
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def get_target_users(self, db: Session, target_uids: List[str], location_filter: Optional[Dict]):
        """Get list of target users based on filters"""
        query = db.query(User)
        
        if target_uids:
            query = query.filter(User.user_uid.in_(target_uids))
        
        if location_filter:
            if location_filter.get('city_id'):
                query = query.filter(User.city_id == location_filter['city_id'])
            elif location_filter.get('district_id'):
                query = query.filter(User.district_id == location_filter['district_id'])
            elif location_filter.get('state_id'):
                query = query.filter(User.state_id == location_filter['state_id'])
        
        return query.all()
    
    async def send_websocket_notifications(self, users: List[User], notification_data: NotificationData):
        """Send real-time WebSocket notifications"""
        message = {
            "type": "notification",
            "title": notification_data.title,
            "message": notification_data.message,
            "notification_type": notification_data.notification_type,
            "priority": notification_data.priority,
            "link_url": notification_data.link_url,
            "data": notification_data.data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user in users:
            await manager.broadcast_to_user(message, user.user_uid)
    
    async def store_in_app_notifications(self, db: Session, users: List[User], notification_data: NotificationData):
        """Store notifications in database"""
        notifications = []
        
        for user in users:
            notification = Notification(
                user_uid=user.user_uid,
                title=notification_data.title,
                message=notification_data.message,
                link_url=notification_data.link_url,
                notification_type=notification_data.notification_type,
                created_at=datetime.utcnow()
            )
            notifications.append(notification)
        
        db.bulk_insert_mappings(Notification, [
            {
                "user_uid": n.user_uid,
                "title": n.title,
                "message": n.message,
                "link_url": n.link_url,
                "notification_type": n.notification_type,
                "created_at": n.created_at
            } for n in notifications
        ])
        db.commit()
    
    async def send_push_notifications(self, users: List[User], notification_data: NotificationData):
        """Send push notifications (Firebase FCM)"""
        # This would integrate with Firebase Cloud Messaging
        # For now, we'll log the push notification
        logger.info(f"Push notification to {len(users)} users: {notification_data.title}")
        
        # In production, you would:
        # 1. Get FCM tokens for users
        # 2. Send via Firebase Admin SDK
        # 3. Handle failed tokens and retry logic
    
    async def send_email_notifications(self, db: Session, users: List[User], notification_data: NotificationData):
        """Send email notifications for important notifications"""
        # Only send email for high priority notifications
        if notification_data.priority not in ["high", "urgent"]:
            return
        
        # Get user preferences to check if email notifications are enabled
        email_enabled_users = []
        for user in users:
            if user.email and self.is_email_notification_enabled(db, user.user_uid):
                email_enabled_users.append(user)
        
        # In production, you would integrate with an email service
        logger.info(f"Email notification to {len(email_enabled_users)} users: {notification_data.title}")
    
    def is_email_notification_enabled(self, db: Session, user_uid: str) -> bool:
        """Check if user has email notifications enabled"""
        # This would check user preferences
        # For now, return True
        return True
    
    async def notify_news_published(self, news: News, location_data: Dict):
        """Notify users when new news is published"""
        notification_data = NotificationData(
            title="📰 New News Published",
            message=f"{news.title[:100]}{'...' if len(news.title) > 100 else ''}",
            notification_type="news_published",
            target_users=[],  # Will be filtered by location
            location_filter=location_data,
            priority="normal" if not news.is_breaking else "high",
            link_url=f"/news/{news.news_uid}",
            data={
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "is_breaking": news.is_breaking
            }
        )
        
        await self.queue_notification(notification_data)
    
    async def notify_breaking_news(self, news: News):
        """Send urgent breaking news notification"""
        notification_data = NotificationData(
            title="🚨 BREAKING NEWS",
            message=news.title,
            notification_type="breaking_news",
            target_users=[],  # Broadcast to all
            priority="urgent",
            link_url=f"/news/{news.news_uid}",
            data={
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "breaking_priority": news.breaking_priority
            }
        )
        
        await self.queue_notification(notification_data)
    
    async def notify_engagement(self, engagement_type: str, news_uid: str, user_uid: str, engagement_data: Dict):
        """Notify about engagement activities"""
        with SessionLocal() as db:
            news = db.query(News).filter(News.news_uid == news_uid).first()
            if not news:
                return
            
            # Notify news author about engagement
            if news.user_uid != user_uid:
                notification_data = NotificationData(
                    title=f"💬 New {engagement_type.title()}",
                    message=f"Someone {engagement_type}d your news: {news.title[:50]}...",
                    notification_type=engagement_type,
                    target_users=[news.user_uid],
                    priority="normal",
                    link_url=f"/news/{news_uid}",
                    data=engagement_data
                )
                
                await self.queue_notification(notification_data)

# Global notification service instance
notification_service = RealTimeNotificationService()
