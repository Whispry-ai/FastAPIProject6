"""
Real-time WebSocket Routes for Hyperlocal News Application
Handles real-time news updates, notifications, and engagement
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import logging

from database import get_db
from websocket_manager import manager
from auth.dependencies import get_current_user
from models.user import User
from models.news import News

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/{user_uid}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_uid: str,
    city_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    state_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time news updates
    Connect to: ws://localhost:8000/ws/{user_uid}?city_id=1&district_id=2&state_id=3
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_uid == user_uid).first()
        if not user:
            await websocket.close(code=4004, reason="User not found")
            return
        
        # Prepare location data
        location_data = {}
        if city_id:
            location_data['city_id'] = city_id
        if district_id:
            location_data['district_id'] = district_id
        if state_id:
            location_data['state_id'] = state_id
        
        # Connect to WebSocket
        await manager.connect(websocket, user_uid, location_data)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_client_message(message, user_uid, websocket, db)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_uid)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_uid)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_uid}: {e}")
        await websocket.close(code=1011, reason="Internal server error")

async def handle_client_message(message: dict, user_uid: str, websocket, db: Session):
    """Handle incoming messages from WebSocket clients"""
    
    message_type = message.get("type")
    
    if message_type == "subscribe_news":
        # Subscribe to news updates for specific location
        location_data = message.get("location", {})
        await handle_news_subscription(user_uid, location_data, db)
        
    elif message_type == "subscribe_engagement":
        # Subscribe to engagement updates for specific news
        news_uid = message.get("news_uid")
        await handle_engagement_subscription(user_uid, news_uid)
        
    elif message_type == "update_location":
        # Update user's location for targeted content
        location_data = message.get("location", {})
        await handle_location_update(user_uid, location_data)
        
    elif message_type == "ping":
        # Keep-alive ping
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    else:
        logger.warning(f"Unknown message type: {message_type}")

async def handle_news_subscription(user_uid: str, location_data: dict, db: Session):
    """Handle subscription to news updates"""
    
    # Get latest news for the subscribed location
    news_query = db.query(News).filter(News.is_approved == 1)
    
    if location_data.get('city_id'):
        news_query = news_query.filter(News.city_id == location_data['city_id'])
    elif location_data.get('district_id'):
        news_query = news_query.filter(News.city.has(district_id=location_data['district_id']))
    elif location_data.get('state_id'):
        news_query = news_query.filter(News.city.has(district_id__state_id=location_data['state_id']))
    
    latest_news = news_query.order_by(News.created_at.desc()).limit(10).all()
    
    # Send latest news to subscriber
    news_data = []
    for news in latest_news:
        news_data.append({
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat(),
            "city_id": news.city_id,
            "breaking_priority": news.breaking_priority
        })
    
    await manager.broadcast_to_user({
        "type": "news_subscription",
        "data": news_data,
        "timestamp": datetime.utcnow().isoformat()
    }, user_uid)

async def handle_engagement_subscription(user_uid: str, news_uid: str):
    """Handle subscription to engagement updates"""
    
    # In a real implementation, track which users are viewing which news
    # For now, just confirm subscription
    await manager.broadcast_to_user({
        "type": "engagement_subscription",
        "news_uid": news_uid,
        "message": "Subscribed to engagement updates",
        "timestamp": datetime.utcnow().isoformat()
    }, user_uid)

async def handle_location_update(user_uid: str, location_data: dict):
    """Handle user location update"""
    
    # Update user's location in manager
    if user_uid in manager.user_locations:
        manager.user_locations[user_uid].update(location_data)
    
    await manager.broadcast_to_user({
        "type": "location_updated",
        "location": location_data,
        "message": "Location updated successfully",
        "timestamp": datetime.utcnow().isoformat()
    }, user_uid)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()

@router.post("/broadcast/news")
async def broadcast_news_update(
    news_data: dict,
    location_data: Optional[dict] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast news update to connected users
    Only accessible by authenticated users (publishers, admins)
    """
    
    # Check user permissions (publisher or admin)
    if current_user.role not in [4, 5]:  # PUBLISHER or ADMIN
        return {"error": "Insufficient permissions"}
    
    await manager.broadcast_news_update(news_data, location_data)
    
    return {
        "message": "News update broadcasted successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/broadcast/breaking")
async def broadcast_breaking_news(
    breaking_news: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast breaking news alert
    Only accessible by admins
    """
    
    # Check user permissions (admin only)
    if current_user.role != 5:  # ADMIN
        return {"error": "Admin access required"}
    
    await manager.broadcast_breaking_news(breaking_news)
    
    return {
        "message": "Breaking news broadcasted successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/broadcast/engagement")
async def broadcast_engagement_update(
    engagement_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast engagement update (like, comment, share)
    """
    
    await manager.broadcast_engagement_update(engagement_data)
    
    return {
        "message": "Engagement update broadcasted successfully",
        "timestamp": datetime.utcnow().isoformat()
    }
