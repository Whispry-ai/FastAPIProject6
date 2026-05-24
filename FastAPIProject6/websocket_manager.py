"""
Real-time WebSocket Manager for Hyperlocal News Application
Handles WebSocket connections, broadcasting, and real-time updates
"""

import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import redis
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Active connections by user
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Connections by location (city_id, district_id, state_id)
        self.location_connections: Dict[str, Set[str]] = {
            'city': set(),
            'district': set(), 
            'state': set()
        }
        # User location mapping
        self.user_locations: Dict[str, Dict] = {}
        # Redis client for pub/sub
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis_client.pubsub()
        
    async def connect(self, websocket: WebSocket, user_uid: str, location_data: Dict = None):
        """Accept WebSocket connection and register user"""
        await websocket.accept()
        
        if user_uid not in self.active_connections:
            self.active_connections[user_uid] = []
        
        self.active_connections[user_uid].append(websocket)
        
        # Store user location for targeted broadcasts
        if location_data:
            self.user_locations[user_uid] = location_data
            
            # Add to location-based groups
            if location_data.get('city_id'):
                self.location_connections['city'].add(f"city_{location_data['city_id']}")
            if location_data.get('district_id'):
                self.location_connections['district'].add(f"district_{location_data['district_id']}")
            if location_data.get('state_id'):
                self.location_connections['state'].add(f"state_{location_data['state_id']}")
        
        logger.info(f"User {user_uid} connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to real-time news feed",
            "timestamp": datetime.utcnow().isoformat(),
            "user_uid": user_uid
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, user_uid: str):
        """Remove WebSocket connection"""
        if user_uid in self.active_connections:
            if websocket in self.active_connections[user_uid]:
                self.active_connections[user_uid].remove(websocket)
            
            # Clean up empty user connections
            if not self.active_connections[user_uid]:
                del self.active_connections[user_uid]
                # Remove from location mapping
                if user_uid in self.user_locations:
                    del self.user_locations[user_uid]
        
        logger.info(f"User {user_uid} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_user(self, message: dict, user_uid: str):
        """Send message to all connections of a specific user"""
        if user_uid in self.active_connections:
            disconnected_connections = []
            
            for connection in self.active_connections[user_uid]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected_connections.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected_connections:
                self.active_connections[user_uid].remove(conn)
    
    async def broadcast_to_location(self, message: dict, location_type: str, location_id: int):
        """Broadcast message to users in specific location"""
        location_key = f"{location_type}_{location_id}"
        
        for user_uid, user_location in self.user_locations.items():
            if user_location.get(f'{location_type}_id') == location_id:
                await self.broadcast_to_user(message, user_uid)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        disconnected_users = []
        
        for user_uid, connections in self.active_connections.items():
            disconnected_connections = []
            
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected_connections.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected_connections:
                connections.remove(conn)
            
            # Mark user for cleanup if no connections left
            if not connections:
                disconnected_users.append(user_uid)
        
        # Clean up users with no connections
        for user_uid in disconnected_users:
            del self.active_connections[user_uid]
            if user_uid in self.user_locations:
                del self.user_locations[user_uid]
    
    async def broadcast_news_update(self, news_data: dict, location_data: dict = None):
        """Broadcast news update to relevant users"""
        message = {
            "type": "news_update",
            "data": news_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if location_data:
            # Send to users in specific location
            if location_data.get('city_id'):
                await self.broadcast_to_location(message, 'city', location_data['city_id'])
            elif location_data.get('district_id'):
                await self.broadcast_to_location(message, 'district', location_data['district_id'])
            elif location_data.get('state_id'):
                await self.broadcast_to_location(message, 'state', location_data['state_id'])
        else:
            # Broadcast to all
            await self.broadcast_to_all(message)
    
    async def broadcast_breaking_news(self, breaking_news: dict):
        """Broadcast breaking news alert"""
        message = {
            "type": "breaking_news",
            "data": breaking_news,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "high"
        }
        
        await self.broadcast_to_all(message)
    
    async def broadcast_engagement_update(self, engagement_data: dict):
        """Broadcast engagement updates (likes, comments, shares)"""
        message = {
            "type": "engagement_update",
            "data": engagement_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to users interested in the specific news
        news_uid = engagement_data.get('news_uid')
        if news_uid:
            # In a real implementation, you'd track who's viewing which news
            await self.broadcast_to_all(message)
    
    def get_connection_stats(self):
        """Get statistics about current connections"""
        return {
            "total_users": len(self.active_connections),
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "location_distribution": {
                location_type: len(connections) 
                for location_type, connections in self.location_connections.items()
            }
        }

# Global connection manager instance
manager = ConnectionManager()
