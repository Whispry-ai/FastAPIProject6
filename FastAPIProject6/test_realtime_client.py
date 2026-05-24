"""
Real-time WebSocket Client Test for Hyperlocal News Application
Tests WebSocket connections and real-time features
"""

import asyncio
import websockets
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeNewsClient:
    """WebSocket client for testing real-time news features"""
    
    def __init__(self, user_uid: str, location_params: dict = None):
        self.user_uid = user_uid
        self.location_params = location_params or {}
        self.websocket = None
        self.connected = False
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            # Build WebSocket URL with location parameters
            ws_url = f"ws://localhost:8000/ws/{self.user_uid}"
            if self.location_params:
                params = []
                if self.location_params.get('city_id'):
                    params.append(f"city_id={self.location_params['city_id']}")
                if self.location_params.get('district_id'):
                    params.append(f"district_id={self.location_params['district_id']}")
                if self.location_params.get('state_id'):
                    params.append(f"state_id={self.location_params['state_id']}")
                if params:
                    ws_url += "?" + "&".join(params)
            
            logger.info(f"Connecting to: {ws_url}")
            
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            logger.info(f"✅ Connected as user {self.user_uid}")
            
            # Start listening for messages
            asyncio.create_task(self.listen())
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
    
    async def listen(self):
        """Listen for WebSocket messages"""
        try:
            while self.connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"❌ Error receiving message: {e}")
    
    async def handle_message(self, data: dict):
        """Handle incoming WebSocket messages"""
        message_type = data.get("type")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        if message_type == "connection":
            logger.info(f"🔗 {data.get('message')}")
        
        elif message_type == "news_update":
            news_data = data.get("data", {})
            logger.info(f"📰 News Update: {news_data.get('title', 'Unknown')}")
        
        elif message_type == "breaking_news":
            breaking_data = data.get("data", {})
            logger.info(f"🚨 BREAKING NEWS: {breaking_data.get('title', 'Unknown')}")
        
        elif message_type == "notification":
            logger.info(f"🔔 Notification: {data.get('title', 'Unknown')}")
        
        elif message_type == "engagement_update":
            engagement_data = data.get("data", {})
            logger.info(f"💬 Engagement: {engagement_data.get('type', 'Unknown')}")
        
        elif message_type == "pong":
            logger.info("🏓 Pong received")
        
        else:
            logger.info(f"📨 Unknown message type: {message_type}")
    
    async def subscribe_to_news(self, location_data: dict = None):
        """Subscribe to news updates"""
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return
        
        message = {
            "type": "subscribe_news",
            "location": location_data or self.location_params
        }
        
        await self.send_message(message)
        logger.info("📰 Subscribed to news updates")
    
    async def subscribe_to_engagement(self, news_uid: str):
        """Subscribe to engagement updates for specific news"""
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return
        
        message = {
            "type": "subscribe_engagement",
            "news_uid": news_uid
        }
        
        await self.send_message(message)
        logger.info(f"💬 Subscribed to engagement updates for {news_uid}")
    
    async def update_location(self, location_data: dict):
        """Update user location"""
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return
        
        message = {
            "type": "update_location",
            "location": location_data
        }
        
        await self.send_message(message)
        logger.info(f"📍 Location updated: {location_data}")
    
    async def send_ping(self):
        """Send ping to keep connection alive"""
        if not self.connected:
            return
        
        message = {"type": "ping"}
        await self.send_message(message)
    
    async def send_message(self, message: dict):
        """Send message to WebSocket server"""
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("🔌 Disconnected from WebSocket")

async def test_multiple_clients():
    """Test multiple WebSocket clients simultaneously"""
    logger.info("🧪 Testing Multiple WebSocket Clients")
    logger.info("=" * 50)
    
    # Create multiple clients with different locations
    clients = [
        RealtimeNewsClient("testuser1", {"city_id": 1, "district_id": 1, "state_id": 1}),
        RealtimeNewsClient("testuser2", {"city_id": 2, "district_id": 2, "state_id": 1}),
        RealtimeNewsClient("admin001", {"city_id": 1, "district_id": 1, "state_id": 1})
    ]
    
    # Connect all clients
    for client in clients:
        await client.connect()
        await asyncio.sleep(1)  # Small delay between connections
    
    # Wait for connections to establish
    await asyncio.sleep(2)
    
    # Test subscriptions
    for i, client in enumerate(clients):
        await client.subscribe_to_news()
        logger.info(f"Client {i+1} subscribed to news")
        await asyncio.sleep(0.5)
    
    # Test location updates
    await clients[0].update_location({"city_id": 3, "district_id": 3, "state_id": 2})
    
    # Test engagement subscription
    await clients[1].subscribe_to_engagement("test_news_123")
    
    # Keep connections alive for testing
    logger.info("🔄 Keeping connections alive for 30 seconds...")
    for i in range(30):
        await asyncio.sleep(1)
        if i % 10 == 0:
            for client in clients:
                await client.send_ping()
    
    # Disconnect all clients
    for client in clients:
        await client.disconnect()
    
    logger.info("✅ Multi-client test completed")

async def test_realtime_features():
    """Test all real-time features"""
    logger.info("🚀 Testing Real-time Features")
    logger.info("=" * 50)
    
    # Create test client
    client = RealtimeNewsClient("testuser123", {"city_id": 1, "state_id": 1})
    
    # Connect and subscribe
    await client.connect()
    await asyncio.sleep(2)
    
    await client.subscribe_to_news()
    await asyncio.sleep(1)
    
    # Test various features
    logger.info("📰 Testing news subscription...")
    await asyncio.sleep(3)
    
    logger.info("📍 Testing location update...")
    await client.update_location({"city_id": 2, "district_id": 2, "state_id": 1})
    await asyncio.sleep(2)
    
    logger.info("💬 Testing engagement subscription...")
    await client.subscribe_to_engagement("sample_news_uid")
    await asyncio.sleep(3)
    
    # Test ping/pong
    logger.info("🏓 Testing ping/pong...")
    for i in range(3):
        await client.send_ping()
        await asyncio.sleep(1)
    
    # Keep connection for testing broadcasts
    logger.info("⏳ Waiting for server broadcasts...")
    await asyncio.sleep(10)
    
    # Disconnect
    await client.disconnect()
    logger.info("✅ Real-time features test completed")

async def main():
    """Main test function"""
    print("🧪 Real-time WebSocket Client Tests")
    print("=" * 50)
    print("Make sure the server is running on localhost:8000")
    print("Run: python main_realtime.py")
    print("=" * 50)
    
    try:
        # Test single client
        await test_realtime_features()
        
        print("\n" + "=" * 50)
        
        # Test multiple clients
        await test_multiple_clients()
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
