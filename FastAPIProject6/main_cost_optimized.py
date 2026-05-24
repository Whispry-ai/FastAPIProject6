"""
Cost-Optimized Hyperlocal News Application
Real-time features using Server-Sent Events (SSE) instead of WebSockets
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
import asyncio
import json
from datetime import datetime

from database import Base, engine
from scheduler import start_notification_cleaner

# Import all route modules
from routes import (
    base_location_routes,
    insights_router,
    user_routes,
    news_routes,
    content_routes,
    engagement_routes,
    guest_routes,
    admin_routes,
    csv_routes
)

# Import AI routes
from routes import ai_routes as ai_router

app = FastAPI(
    title="Hyperlocal News API - Cost Optimized",
    description="Hyperlocal news application with Server-Sent Events",
    version="1.0.0"
)

# SessionMiddleware (required for Google OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-session-key",
    same_site="lax",
    https_only=False
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (only once)
Base.metadata.create_all(bind=engine)

# Start background tasks
start_notification_cleaner()

# Include all routers
app.include_router(base_location_routes.router, prefix="/base", tags=["Base Location"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])
app.include_router(news_routes.router, prefix="/news", tags=["News"])
app.include_router(content_routes.router, prefix="/content", tags=["Content"])
app.include_router(engagement_routes.router, prefix="/engagement", tags=["Engagement"])
app.include_router(guest_routes.router, prefix="/guest", tags=["Guest"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
app.include_router(csv_routes.router, prefix="/csv", tags=["CSV"])
app.include_router(insights_router.router, prefix="/insights", tags=["Insights"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# Simple SSE endpoint for real-time updates
@app.get("/events")
async def event_stream():
    """Server-Sent Events endpoint for real-time updates"""
    
    async def event_generator():
        # This is a simple example - in production, you'd connect to your database
        # and send real updates when they happen
        
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to real-time updates'})}\n\n"
        
        # Simulate some real-time updates (replace with actual data)
        for i in range(5):
            await asyncio.sleep(2)  # Wait 2 seconds
            
            event_data = {
                'type': 'news_update',
                'data': {
                    'news_uid': f'news_{i}',
                    'title': f'Sample News {i+1}',
                    'message': f'This is sample news update {i+1}',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
        
        # Send disconnect event
        yield f"data: {json.dumps({'type': 'disconnected', 'message': 'Stream ended'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hyperlocal News API - Cost Optimized</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #333;
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                max-width: 800px;
            }
            h1 {
                color: #0077b6;
                margin-bottom: 30px;
            }
            .status {
                background: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                display: inline-block;
                margin: 10px 0;
            }
            .feature {
                margin: 20px 0;
                padding: 15px;
                border-left: 4px solid #3498db;
                background: #ecf0f1;
                text-align: left;
            }
            .feature h3 {
                color: #3498db;
                margin-bottom: 10px;
            }
            .cost-info {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }
            .endpoint {
                background: #e8f5e8;
                padding: 5px 10px;
                border-radius: 3px;
                font-family: monospace;
                margin: 5px 0;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Hyperlocal News API - Cost Optimized</h1>
            <div class="status">✅ Server Running (Cost Optimized)</div>
            
            <div class="cost-info">
                <h3>💰 Cost Optimization Features:</h3>
                <p><strong>Server-Sent Events (SSE)</strong> instead of WebSockets</p>
                <p><strong>Reduced Memory Usage</strong> - No persistent connections</p>
                <p><strong>Lower CPU Usage</strong> - Event-driven updates</p>
                <p><strong>Scalable</strong> - HTTP-based streaming</p>
            </div>
            
            <div class="feature">
                <h3>📰 Core Features</h3>
                <p>News creation, management, and distribution</p>
                <div class="endpoint">/news/*</div>
            </div>
            
            <div class="feature">
                <h3>👥 User Management</h3>
                <p>Registration, authentication, and profiles</p>
                <div class="endpoint">/user/*</div>
            </div>
            
            <div class="feature">
                <h3>🤖 AI Analysis</h3>
                <p>Sentiment, fake news detection, categorization</p>
                <div class="endpoint">/ai/*</div>
            </div>
            
            <div class="feature">
                <h3>📊 Analytics</h3>
                <p>News insights and user statistics</p>
                <div class="endpoint">/insights/*</div>
            </div>
            
            <div class="feature">
                <h3>🌐 Real-time Events</h3>
                <p>Server-Sent Events for live updates</p>
                <div class="endpoint">GET /events</div>
            </div>
            
            <h3>📖 Documentation</h3>
            <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
            
            <h3>🏥 Health Check</h3>
            <p><a href="/health">System Health Status</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hyperlocal-news-cost-optimized",
        "version": "1.0.0",
        "real_time_type": "Server-Sent Events",
        "cost_optimization": "enabled",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "news_management": True,
            "user_management": True,
            "ai_features": True,
            "analytics": True,
            "real_time_events": True,
            "websocket": False,
            "sse": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_cost_optimized:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
